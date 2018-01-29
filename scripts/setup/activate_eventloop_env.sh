#!/usr/bin/env bash

BUILD_DIR="${RNN_TAUID_ROOT}/env/build-eventloop"

if [ -d "${BUILD_DIR}" ]; then
    echo "Setting up eventloop environment"
    if [ ! -z ${ATLAS_LOCAL_ROOT_BASE+x} ]; then
        source "${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh" --quiet
    else
        echo "Cannot setup AnalysisBase on non-cvmfs enabled devices"
        return 1
    fi

    asetup "${RNN_TAUID_ASETUP}"
    source "${BUILD_DIR}/${AnalysisBase_PLATFORM}/setup.sh"
else
    echo "Eventloop algorithms not compiled - call setup_eventloop.sh first"
    return 1
fi
