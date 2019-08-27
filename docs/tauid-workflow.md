# Tau Identification

The following describes the workflow to train the RNN-based tau identification
algorithm.

## Producing MxAOD with THOR

Training the RNN-based tau identification requires MxAODs produced with THOR. A
predefined stream called `StreamRNNTauID` is available in THOR which calls the
decorator `RNNTauIDVarsCalculator` from tauRecToolsDev. Make sure to point
the `THOR_SHARE` variable to the corresponding THOR directory. Before running,
make sure that the THOR stream is configured to run the `RNNTauIDVarsCalculator`.

```bash
# THOR_SHARE needs to be set to THOR's share directory
thor ${THOR_SHARE}/StreamRNNTauID/Main.py -r grid \
    -g ${THOR_SHARE}/datasets/MC16DGammatautau.txt \
    --gridstreamname StreamRNNTauID --gridrunversion 01-00

thor ${THOR_SHARE}/StreamRNNTauID/Main.py -r grid \
    -g ${THOR_SHARE}/datasets/MC16DDijetSamples.txt \
    --gridstreamname StreamRNNTauID --gridrunversion 01-00
```

This will produce MxAODs for the Gammatautau sample as well as jet slices JZ1W to JZ6W.

For details on how to use THOR consult the
[documentation](https://gitlab.cern.ch/atlas-perf-tau/THOR/blob/master/README.rst).

## Flattening the MxAOD

After downloading the MxAODs in the directory `${STREAM_DIR}` (should contain a
subdirectory for every sample) the MxAOD flattening can be run with:

```bash
# Set up environment variables
source rnn-tauid/setup.sh

# Compile the EventLoop algorithms (only if not done beforehand or EventLoop
# algs were changed)
setup_eventloop.sh

# Activate the EventLoop enviroment for the current shell
source activate_eventloop_env.sh

# Gammatautau
RunNtupleCreator.py --tauid ${STREAM_DIR} "*Gammatautau*" -d Gammatautau \
    -o Gammatautau.root --truth

# JZ1W
RunNtupleCreator.py --tauid ${STREAM_DIR} "*JZ1W*" -d JZ1W -o JZ1W.root

# JZ2W
RunNtupleCreator.py --tauid ${STREAM_DIR} "*JZ2W*" -d JZ2W -o JZ2W.root

# ...
```

Afterwards a separate flat ntuple should be available for every input sample (as
well as Eventloop submission directories which can be deleted). The `--truth`
flag ensures that the tau truth information needed for training is written out.

## Converting to HDF5 for Training

The following converts the ntuples to HDF5 format for training the networks. A
basic tau candidate selection, given by the second positional argument, is
applied. Additional selections can be passed as a string in `--sel`.

```bash
# Set up environment variables
source rnn-tauid/setup.sh

# Create python environment and install necessary packages
setup_python.sh

# Activate python environment
source activate_python_env.sh

# Convert ntuple to hdf5
TRAIN_SEL="TauJets.mcEventNumber % 2 == 0"
TEST_SEL="TauJets.mcEventNumber % 2 == 1"

# A running index is given by '%d' to split files
ntuple2hdf.py sig1P_train_%d.h5 truth1p ${NTUPLE_DIR}/*Gammatautau*.root \
    --sel "${TRAIN_SEL}"

ntuple2hdf.py sig3P_train_%d.h5 truth3p ${NTUPLE_DIR}/*Gammatautau*.root \
    --sel "${TRAIN_SEL}"

ntuple2hdf.py bkg1P_train_%d.h5 1p ${NTUPLE_DIR}/*JZ?W*.root \
    --sel "${TRAIN_SEL}"

ntuple2hdf.py bkg3P_train_%d.h5 3p ${NTUPLE_DIR}/*JZ?W*.root \
    --sel "${TRAIN_SEL}"

# Repeat for 'TEST_SEL'
```

The datasets are split into a training and testing part according to the
`mcEventNumber`. This ensures that training / testing events can be identified
in subsequent THOR productions (e.g. when applying a new network in THOR).


## Model Training

The model training can be performed in a standalone python environment (no CVMFS
required). Alternatively, activate the pre-built python environment. Training
the experimental setup (the one provided with the AODFix) can be done with:

```bash
# Train 1-prong network
train_experimental.py ${HDF_DIR}/sig1P_train_%d.h5 ${HDF_DIR}/bkg1P_train_%d.h5

# Train 3-prong network (will overwrite outputs of the 1-prong training)
train_experimental.py ${HDF_DIR}/sig3P_train_%d.h5 ${HDF_DIR}/bkg3P_train_%d.h5
```

The training process generates two output files `model.h5` and `preproc.h5`
containing the model weights / architecture and the preprocessing rules for the
input variables. These two files fully define the network and can be used for
evaluation at a later stage.

## Model Evaluation

## Converting the Model for tauRecTools

To convert the model into a form that is suitable to run in the tauRecTool used
to evaluate the model in the ATLAS software framework a clean shell is required.
This is because `lwtnn`, which is used to evaluate the networks in C++, is only
available for python3, while most of the ATLAS infrastructure runs on python2.
To activate the python3 environment and convert the model do this:

```bash
source rnn-tauid/setup.sh

# Activate the lwtnn python3 environment
source activate_lwtnn_env.sh

# Split the model file returned by training into architecture.json and weights.h5
lwtnn-split-keras-network.py model.h5

# Fill the lwtnn variable specification
kerasfunc2json.py architecture.json weights.h5 \
   | fill-lwtnn-varspec.py preproc.h5 \
   | kerasfunc2json.py architecture.json weights.h5 /dev/stdin > tauid_nn.json
```

A quick explanation of the different parts of the conversion:

- `lwtnn-split-keras-network.py` splits the output of the training into a
  `json` file describing the model architecture and a HDF5 file that contains
  the weights of the different layers.

- The first invocation of `kerasfunc2json.py` writes an input variable
  specification to stdout. This description has to be configured with the names
  of the variables, layer names, and offset and scales that are used by the
  usual preprocessing.

- The variable description can be automatically filled using
  `fill-lwtnn-varspec.py`. The preprocessing offsets and scales as
  well as variable names are taken from the preprocessing output of the training.

- Finally, lwtnn compiles the (filled) variable specification, architecture and
  weights of the network into a single json representation which can be used in
  `TauJetRNNEvaluator`.

A template for running the tau identification in THOR can be found in
`THOR/share/StreamRNNTauID`. If the trained and converted model is placed in
`tauRecTools/share`, then the model can be evaluated in THOR by scheduling the
`TauJetRNNEvaluator` and setting its properties. An example is:

```python
# Evaluator for RNN Tau-ID
Clf = ROOT.tauRecTools.TauJetRNNEvaluator("TauJetRNNEvaluator")

# Input files and output score
CHECK(Clf.setProperty("NetworkFile1P", "tauRecTools/my_net_1p.json"))
CHECK(Clf.setProperty("NetworkFile3P", "tauRecTools/my_net_3p.json"))
CHECK(Clf.setProperty("OutputVarname", "RNNJetScore"))

# Only taus with at least one track
CHECK(Clf.setProperty("MinChargedTracks", 1))

# Configuration for object selection
CHECK(Clf.setProperty("MaxTracks", 10))
CHECK(Clf.setProperty("MaxClusters", 6))
CHECK(Clf.setProperty("MaxClusterDR", 1.0))

# Specification of layer/node names
CHECK(Clf.setProperty("InputLayerScalar", "scalar"))
CHECK(Clf.setProeprty("InputLayerTracks", "tracks"))
CHECK(Clf.setProperty("InputLayerClusters", "clusters"))
CHECK(Clf.setProperty("OutputLayer", "rnnid_output"))
CHECK(Clf.setProperty("OutputNode", "sig_prob"))

Config += Clf
```

This will decorate the RNN jet score for each tau candidate with at least one track.
