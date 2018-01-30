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

# Setup paths for lwtnn
LWTNN_SCRIPTS_DIR="${RNN_TAUID_ROOT}/src/lwtnn/scripts"
LWTNN_CONVERTERS_DIR="${RNN_TAUID_ROOT}/src/lwtnn/converters"

if [ ! -d "${LWTNN_SCRIPTS_DIR}" ]; then
    echo "Cannot find lwtnn scripts directory -- clone with --recursive"
fi

if [ ! -d "${LWTNN_CONVERTERS_DIR}" ]; then
    echo "Cannot find lwtnn converters directory -- clone with --recursive"
fi

export PATH="${LWTNN_SCRIPTS_DIR}:${PATH}"
export PATH="${LWTNN_CONVERTERS_DIR}:${PATH}"
