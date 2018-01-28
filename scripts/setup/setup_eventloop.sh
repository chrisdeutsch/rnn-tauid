#!/usr/bin/env bash

# Configuration
BUILD_DIR="${RNN_TAUID_ROOT}/env/build-eventloop"

echo "Setting up eventloop algorithms"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

if [ ! -z ${ATLAS_LOCAL_ROOT_BASE+x} ]; then
    source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh --quiet
    asetup "${RNN_TAUID_ASETUP}"
    cmake "${RNN_TAUID_ROOT}/src/eventloop/"
    make
else
    echo "Cannot setup AnalysisBase on non-cvmfs enabled devices"
fi
