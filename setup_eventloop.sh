#!/usr/bin/env bash

# Configuration
ASETUP_STRING="21.2.12,AnalysisBase"

# Path of the directory containing the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="${SCRIPT_DIR}/../build-$(basename "${SCRIPT_DIR}")"
CURRENT_DIR="$(pwd)"

export PATH="${SCRIPT_DIR}/scripts:${PATH}"

echo "Using build directory: ${BUILD_DIR}"
if [ ! -d "${BUILD_DIR}" ]; then
    mkdir "${BUILD_DIR}"
fi

cd "${BUILD_DIR}"

setupATLAS --quiet
asetup "${ASETUP_STRING}"

cmake "${SCRIPT_DIR}/src/eventloop/"
source "${AnalysisBase_PLATFORM}/setup.sh"
make

cd "${CURRENT_DIR}"
