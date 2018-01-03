#!/usr/bin/env bash

# Configuration
ROOT_VERSION="6.08.06-x86_64-slc6-gcc62-opt"
MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh"
CONDA_PATH="${HOME}/miniconda2"
CONDA_ENV="rnn-tauid"

# Packages for first time setup
CONDA_PKGS="numpy scipy h5py keras tqdm"
PIP_PKGS="root_numpy" # conda version is outdated

# Path of the directory containing the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Setting up root
if [[ -x "$(command -v setupATLAS)" ]]; then
    setupATLAS --quiet
    lsetup "root ${ROOT_VERSION}"
    HAS_ROOT=1
else
    echo "setupATLAS not available - setup environment without root"
fi

# Activate / install conda
if [[ -d "${CONDA_PATH}" ]]; then
    echo "Conda found in ${CONDA_PATH}"
else
    echo "Downloading miniconda..."
    curl -s -S "${MINICONDA_URL}" > miniconda.sh
    echo "Installing miniconda..."
    bash miniconda.sh -b -p "${CONDA_PATH}"
    rm miniconda.sh
    echo "Installed miniconda in ${CONDA_PATH}"
fi

# Activate / create python environment
export PATH="${CONDA_PATH}/bin:${PATH}"

if [[ -d "${CONDA_PATH}/envs/${CONDA_ENV}" ]]; then
    echo "Activating environment: ${CONDA_ENV}"
    source activate ${CONDA_ENV}
else
    echo "Creating environment: ${CONDA_ENV}"
    conda create -q -y -n ${CONDA_ENV} python=2 ${CONDA_PKGS}
    source activate ${CONDA_ENV}

    if [ "${HAS_ROOT}" ]; then
        pip install ${PIP_PKGS}
    else
        echo "Skipping installation of root_numpy - Will not be able to read root files"
    fi
fi

# Setting PATHs
export PATH="${SCRIPT_DIR}/scripts:${PATH}"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"
