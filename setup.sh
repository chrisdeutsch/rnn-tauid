# Path of the directory containing the script
export RNN_TAUID_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# AnalysisBase setup
export RNN_TAUID_ASETUP="21.2.12,AnalysisBase"

# Python environment setup
export RNN_TAUID_ROOT_VERSION="6.08.06-x86_64-slc6-gcc62-opt"
export RNN_TAUID_CONDA_PATH="${RNN_TAUID_ROOT}/env/miniconda2"
export RNN_TAUID_CONDA_ENV="rnn-tauid"
export RNN_TAUID_CONDA_ENV_LWTNN="lwtnn"

# Setting PATHs
export PATH="${RNN_TAUID_ROOT}/scripts:${PATH}"
export PATH="${RNN_TAUID_ROOT}/scripts/setup:${PATH}"
export PYTHONPATH="${RNN_TAUID_ROOT}/src:${PYTHONPATH}"
