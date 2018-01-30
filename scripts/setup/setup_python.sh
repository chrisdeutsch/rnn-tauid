#!/usr/bin/env bash

# Configuration
MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh"
CONDA_ENV="rnn-tauid"
RNN_TAUID_CONDA_ENV_LWTNN="lwtnn"

# Packages for first time setup
CONDA_PKGS="numpy scipy h5py keras tqdm scikit-learn matplotlib"
CONDA_PKGS_LWTNN="keras h5py"
PIP_PKGS="root_numpy" # conda version is outdated


echo "Setting up python environments"

# Create env directory if it does not exist
mkdir -p "${RNN_TAUID_ROOT}/env"

# Setting up root
if [ ! -z ${ATLAS_LOCAL_ROOT_BASE+x} ];then
    source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh --quiet
    lsetup "root ${RNN_TAUID_ROOT_VERSION}"
    HAS_ROOT=1
else
    echo "setupATLAS not available - setup environment without root"
fi

# Activate / install conda
if [[ -d "${RNN_TAUID_CONDA_PATH}" ]]; then
    echo "Conda found in ${RNN_TAUID_CONDA_PATH}"
else
    echo "Downloading miniconda..."
    curl -s -S "${MINICONDA_URL}" > "${RNN_TAUID_ROOT}/env/miniconda.sh"
    echo "Installing miniconda..."
    bash "${RNN_TAUID_ROOT}/env/miniconda.sh" -b -p "${RNN_TAUID_CONDA_PATH}"
    rm "${RNN_TAUID_ROOT}/env/miniconda.sh"
    echo "Installed miniconda in ${RNN_TAUID_CONDA_PATH}"
fi

# Activate / create python environment
export PATH="${RNN_TAUID_CONDA_PATH}/bin:${PATH}"

# Setup training environment (python2)
if [[ ! -d "${RNN_TAUID_CONDA_PATH}/envs/${RNN_TAUID_CONDA_ENV}" ]]; then
    echo "Creating environment: ${RNN_TAUID_CONDA_ENV}"
    conda create -q -y -n ${RNN_TAUID_CONDA_ENV} python=2 ${CONDA_PKGS}
    source activate ${RNN_TAUID_CONDA_ENV}

    if [ "${HAS_ROOT}" ]; then
        pip install ${PIP_PKGS}
    else
        echo "Skipping installation of root_numpy - Will not be able to read root files"
    fi

    source deactivate
else
    echo "Environment ${RNN_TAUID_CONDA_ENV} already exists - skipping"
fi

# Setup lwtnn environment (python3)
if [[ ! -d "${RNN_TAUID_CONDA_PATH}/envs/${RNN_TAUID_CONDA_ENV_LWTNN}" ]]; then
    echo "Creating environment: ${RNN_TAUID_CONDA_ENV_LWTNN}"
    conda create -q -y -n ${RNN_TAUID_CONDA_ENV_LWTNN} python=3 ${CONDA_PKGS_LWTNN}
    source activate ${RNN_TAUID_CONDA_ENV_LWTNN}
else
    echo "Environment ${RNN_TAUID_CONDA_ENV_LWTNN} already exists - skipping"
fi
