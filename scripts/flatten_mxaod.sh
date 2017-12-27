#!/usr/bin/env bash

MXAOD_DIR="MxAOD_v11/"
OUTDIR="ntuples/"
FLAGS="--rnnscore -n 100000"

echo "Input MxAOD directory: $MXAOD_DIR"
echo "Flags for NtupleCreator: $FLAGS"

if [ ! -d "$OUTDIR" ]; then
    echo "Creating output directory: $OUTDIR"
    mkdir $OUTDIR
else
    echo "Using preexisting output directory: $OUTDIR"
    echo "WARNING: will overwrite any samples located in directory"
fi

# JZ1W
RunNtupleCreator.py $MXAOD_DIR "*JZ1W*" -d JZ1W $FLAGS
mv JZ1W/data-ntuple/*.root $OUTDIR/JZ1W.root
rm -rf JZ1W/

# JZ2W
RunNtupleCreator.py $MXAOD_DIR "*JZ2W*" -d JZ2W $FLAGS
mv JZ2W/data-ntuple/*.root $OUTDIR/JZ2W.root
rm -rf JZ2W/

# JZ3W
#RunNtupleCreator.py $MXAOD_DIR "*JZ3W*" -d JZ3W $FLAGS
#mv JZ3W/data-ntuple/*.root $OUTDIR/JZ3W.root
#rm -rf JZ3W/

# Gammatautau
#RunNtupleCreator.py $MXAOD_DIR "*Gammatautau*" -d Gammatautau --truth $FLAGS
#mv Gammatautau/data-ntuple/*.root $OUTDIR/Gammatautau.root
#rm -rf Gammatautau/