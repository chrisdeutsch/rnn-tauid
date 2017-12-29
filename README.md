# RNN-TauID

## Installation

Requires:
- numpy
- root_numpy
- h5py
- scipy
- keras
- tensorflow
- tqdm

### Training environment

Suggest to setup using conda (install everything into root environment):

First time setup for cvmfs-enabled devices:
```
setupATLAS --quiet
lsetup -q "root 6.08.06-x86_64-slc6-gcc62-opt"

curl https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh > miniconda.sh
bash miniconda.sh -b -p $HOME/testconda
rm miniconda.sh

export PATH="$HOME/testconda/bin:$PATH"

# Alternatively activate your favorite environment

CONDA_PKGS="numpy scipy h5py keras tqdm"
PIP_PKGS="root_numpy" # conda version is outdated

conda install -q -y $CONDA_PKGS
pip install $PIP_PKGS
```
Note: Suggest compiling tensorflow from source to enable AVX, SSE etc. for reduced training time

See `requirements.txt` for the latest requirements including version numbers.

Activate environment:
```
setupATLAS --quiet
lsetup -q "root 6.08.06-x86_64-slc6-gcc62-opt"
export PATH="$HOME/testconda/bin:$PATH"
export PATH="$HOME/rnnid-pkg/scripts:$PATH" # TODO: Fixme
export PYTHONPATH="$HOME/rnnid-pkg/src:$PYTHONPATH" # TODO: Fixme
```

### Eventloop algorithms

```
mkdir ../build
cd ../build

setupATLAS --quiet
asetup 21.2.12,AnalysisBase
cmake ../rnn-tauid/src/eventloop/
source ${AnalysisBase_PLATFORM}/setup.sh
make
```

Activate environment (from build directory):
```
setupATLAS --quiet
asetup 21.2.12,AnalysisBase
source ${AnalysisBase_PLATFORM}/setup.sh
```

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

## TODOs

- Implement the most important plots for performance evaluation
    - Create subpackage for plotting incl. a plot class for defining the plots
    - Partial dependence plots?
    - Always save raw data to recreate the plot (pickle?)
- Port training implementation
- Write an evaluator using lwtnn and eventloop (produce slim MxAOD output)
- Write a one-shot script to do everything