# Tau Decay Mode Classification

The following describes the workflow to train the RNN-based decay mode
classification algorithm for taus.

## Producing MxAOD with THOR

Training the RNN-based decay mode classification requires training samples
produced with THOR. For this a decorator called `DecayModeIDDecorator` from
`tauRecToolsDev` is run inside of THOR that decorates the required variables. A
preconfigured stream called `StreamDecayModeClf` is available in THOR. An
example invokation of THOR is given here: 

```bash
# THOR_SHARE needs to be set to THOR's share directory
thor ${THOR_SHARE}/StreamDecayModeClf/Main.py -r grid \
    -g ${THOR_SHARE}/datasets/MC16DGammatautau.txt \
    --gridstreamname StreamDecayModeClf --gridrunversion 01-00
```

For details on how to use THOR consult the
[documentation](https://gitlab.cern.ch/atlas-perf-tau/THOR/blob/master/README.rst).

## Flattening the MxAOD

After downloading the samples with `rucio` in the directory `${STREAM_DIR}`
(should contain a subdirectory for the Gammatautau sample) the MxAOD flattening
can be run with:

```bash
# Set up environment variables
source rnn-tauid/setup.sh

# Compile the EventLoop algorithms (only if not done beforehand or EventLoop
# algs were changed)
setup_eventloop.sh

# Activate the EventLoop enviroment for the current shell
source activate_eventloop_env.sh

# Run the flattening (output: Gammatautau.root, Gammatautau_1.root, etc.)
RunNtupleCreator.py --decaymodeclf --truth \
    ${STREAM_DIR}/ "*Gammatautau*" -o Gammatautau.root
```

## Converting to HDF5 for Training

After creating flat ntuples from the MxAOD they have to be further converted
into HDF5 format for convenient processing in python. This step requires ROOT
and root_numpy to read the ntuples. As a result a CVMFS-enabled machine is
required for this step. Alternatively you can use your own python setup as long
as all requirements are fulfilled.

To convert the ntuples execute the following in a clean shell:

```bash
# Set up environment variables
source rnn-tauid/setup.sh

# Create python environment and install necessary packages
setup_python.sh

# Activate python environment
source activate_python_env.sh

# Convert ntuple to hdf5
SEL="(TauJets.truthDecayMode < 5) && (TauJets.pt < 100000) && (TauJets.truthPtVis < 100000)"
TRAIN_SEL="(TauJets.mcEventNumber % 2 == 0) && ${SEL}"
TEST_SEL="(TauJets.mcEventNumber % 2 == 1) && ${SEL}"

# A running index is given by '%d' to split files
ntuple2hdf.py gammatautau_train_%d.h5 truthXp ${NTUPLE_DIR}/Gammatautau*.root \
    --decaymodeclf --treename tree --sel "${TRAIN_SEL}"

ntuple2hdf.py gammatautau_test_%d.h5 truthXp ${NTUPLE_DIR}/Gammatautau*.root \
    --decaymodeclf --treename tree --sel "${TEST_SEL}"
```

This applies a basic tau selection for decay mode classification and splits the
dataset into a training and testing part according to the `mcEventNumber`.

## Model Training

The model training can be performed in a standalone python environment (no CVMFS
required). Training the default setup can be done with:

```bash
train_decaymodeclf.py gammatautau_train_%d.h5
```

The training process generates two output files `model.h5` and `preproc.h5`
containing the model weights / architecture and the preprocessing rules for the
input variables. These two files fully define the network and can be used for
evaluation at a later stage.
