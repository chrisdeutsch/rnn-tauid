#!/usr/bin/env bash

MXAOD_DIR="MxAOD_v11/"
OUTDIR="ntuples_v11/"
FLAGS="--rnnscore"

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
RunNtupleCreator.py $MXAOD_DIR "*JZ3W*" -d JZ3W $FLAGS
mv JZ3W/data-ntuple/*.root $OUTDIR/JZ3W.root
rm -rf JZ3W/

# JZ4W
RunNtupleCreator.py $MXAOD_DIR "*JZ4W*" -d JZ4W $FLAGS
mv JZ4W/data-ntuple/*.root $OUTDIR/JZ4W.root
rm -rf JZ4W/

# JZ5W
RunNtupleCreator.py $MXAOD_DIR "*JZ5W*" -d JZ5W $FLAGS
mv JZ5W/data-ntuple/*.root $OUTDIR/JZ5W.root
rm -rf JZ5W/

# JZ6W
RunNtupleCreator.py $MXAOD_DIR "*JZ6W*" -d JZ6W $FLAGS
mv JZ6W/data-ntuple/*.root $OUTDIR/JZ6W.root
rm -rf JZ6W/

# Gammatautau
RunNtupleCreator.py $MXAOD_DIR "*Gammatautau*" -d Gammatautau --truth $FLAGS
mv Gammatautau/data-ntuple/*.root $OUTDIR/Gammatautau.root
rm -rf Gammatautau/
