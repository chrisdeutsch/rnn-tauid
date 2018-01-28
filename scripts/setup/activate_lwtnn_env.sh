#!/usr/bin/env bash

# Setting up conda and virtual environment
if [[ -d "${RNN_TAUID_CONDA_PATH}" ]]; then
    echo "Conda found in ${RNN_TAUID_CONDA_PATH}"
    export PATH="${RNN_TAUID_CONDA_PATH}/bin:${PATH}"
    echo "Activating environment: ${RNN_TAUID_CONDA_ENV_LWTNN}"
    source activate "${RNN_TAUID_CONDA_ENV_LWTNN}"
else
    echo "Conda not found - aborting"
    return 1
fi
