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

In a clean shell

This step requires a cvmfs-enabled machine.

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

ntuple2hdf.py gammatautau_train_%d.h5 truthXp ${NTUPLE_DIR}/Gammatautau*.root \
    --decaymodeclf --treename tree --sel "${TRAIN_SEL}"

ntuple2hdf.py gammatautau_test_%d.h5 truthXp ${NTUPLE_DIR}/Gammatautau*.root \
    --decaymodeclf --treename tree --sel "${TEST_SEL}"
```
