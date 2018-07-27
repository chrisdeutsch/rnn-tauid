# Tau Identification

The following describes the workflow to train the RNN-based tau identification
algorithm.

## Producing MxAOD with THOR

Training the RNN-based tau identification requires MxAODs produced with THOR. A
predefined stream called `StreamRNNTauID` is available in THOR which calls the
decorator `RNNTauIDVarsCalculator` from tauRecToolsDev.

```bash
# THOR_SHARE needs to be set to THOR's share directory
thor ${THOR_SHARE}/StreamRNNTauID/Main.py -r grid \
    -g ${THOR_SHARE}/datasets/MC16DGammatautau.txt \
    --gridstreamname StreamRNNTauID --gridrunversion 01-00

thor ${THOR_SHARE}/StreamRNNTauID/Main.py -r grid \
    -g ${THOR_SHARE}/datasets/MC16DDijetSamples.txt \
    --gridstreamname StreamRNNTauID --gridrunversion 01-00
```

This should result in MxAODs for the Gammatautau samples as well as jet slices JZ1W to JZ6W.

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
well as Eventloop submission directories which can be deleted).

## Converting to HDF5 for Training

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

This applies the default tau selection and splits the datasets into training and
testing part according to the `mcEventNumber`.

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
