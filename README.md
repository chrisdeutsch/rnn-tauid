# RNN-TauID

## Installation

Requires:
- numpy
- root_numpy
- h5py
- scipy
- keras
- tensorflow

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

CONDA_PKGS="numpy scipy h5py keras"
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
```

TODO: Add scripts directory to path

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
