# Quick Start

You can find the code on [Gitlab](https://gitlab.cern.ch/cdeutsch/rnn-tauid).

TODO: Comment on the use of different environments

## Installation

# RNN-TauID

## Setup

1. Set enviroment variables with `source setup.sh`
2. Compile eventloop variables with `setup_eventloop.sh` (optional)
3. Create python environments with `setup_python.sh` (optional)
4. Activate environments with `source activate_*_env.sh` where `*` is
   `eventloop`, `python` or `lwtnn`

## Workflow

1. Produce MxAODs on the grid with THOR
2. Flatten MxAODs
3. Produce hdf5 files for training
4. Train
5. Evaluate

## Related packages

- [THOR](https://gitlab.cern.ch/cdeutsch/THOR/tree/RNN-MC16A)
- [tauRecToolsDev](https://gitlab.cern.ch/cdeutsch/tauRecToolsDev/tree/RNN-MC16A)

TODO: Explain workflow including external packages

## Convert trained model

```
# Setup the environment
source rnn-tauid/setup.sh

# Creates required python environments (can be omitted if they already exist)
setup_python.sh

# Activates the python environment needed for the lwtnn converter
source activate_lwtnn_env.sh

# Splits the model.h5 into separate architecture and weight files
lwtnn-split-keras-network.py model.h5

# Create the network tuning (fill-lwtnn-varspec.py fills the variable
# specification including variable names, variable scales/offsets and
# input/output layer config)
kerasfunc2json.py architecture.json weights.h5 | fill-lwtnn-varspec.py preproc.h5 | kerasfunc2json.py architecture.json weights.h5 /dev/stdin > nn.json
```
