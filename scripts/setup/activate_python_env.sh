#!/usr/bin/env bash

# Setting up root
if [ ! -z ${ATLAS_LOCAL_ROOT_BASE+x} ];then
    source "${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh" --quiet
    lsetup "root ${RNN_TAUID_ROOT_VERSION}"
    HAS_ROOT=1
else
    echo "setupATLAS not available - setup environment without root"
fi

# Setting up conda and virtual environment
if [[ -d "${RNN_TAUID_CONDA_PATH}" ]]; then
    echo "Conda found in ${RNN_TAUID_CONDA_PATH}"
    export PATH="${RNN_TAUID_CONDA_PATH}/bin:${PATH}"
    echo "Activating environment: ${RNN_TAUID_CONDA_ENV}"
    source activate "${RNN_TAUID_CONDA_ENV}"
else
    echo "Conda not found - aborting"
    return 1
fi
