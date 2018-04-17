#!/usr/bin/env bash
set -e

MXAOD_DIR="RnnTrack_TauID/"
OUTDIR="ntuples_max/"
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
mkdir JZ1W-ntuples
RunNtupleCreator.py $MXAOD_DIR "*JZ1W*" -d JZ1W -o JZ1W-ntuples/JZ1W.root $FLAGS
mv JZ1W-ntuples/*.root $OUTDIR/
rm -rf JZ1W/ JZ1W-ntuples/

# JZ2W
mkdir JZ2W-ntuples
RunNtupleCreator.py $MXAOD_DIR "*JZ2W*" -d JZ2W -o JZ2W-ntuples/JZ2W.root $FLAGS
mv JZ2W-ntuples/*.root $OUTDIR/
rm -rf JZ2W/ JZ2W-ntuples/

# JZ3W
mkdir JZ3W-ntuples
RunNtupleCreator.py $MXAOD_DIR "*JZ3W*" -d JZ3W -o JZ3W-ntuples/JZ3W.root $FLAGS
mv JZ3W-ntuples/*.root $OUTDIR/
rm -rf JZ3W/ JZ3W-ntuples/

# JZ4W
mkdir JZ4W-ntuples
RunNtupleCreator.py $MXAOD_DIR "*JZ4W*" -d JZ4W -o JZ4W-ntuples/JZ4W.root $FLAGS
mv JZ4W-ntuples/*.root $OUTDIR/
rm -rf JZ4W/ JZ4W-ntuples/

# JZ5W
mkdir JZ5W-ntuples
RunNtupleCreator.py $MXAOD_DIR "*JZ5W*" -d JZ5W -o JZ5W-ntuples/JZ5W.root $FLAGS
mv JZ5W-ntuples/*.root $OUTDIR/
rm -rf JZ5W/ JZ5W-ntuples/

# JZ6W
mkdir JZ6W-ntuples
RunNtupleCreator.py $MXAOD_DIR "*JZ6W*" -d JZ6W -o JZ6W-ntuples/JZ6W.root $FLAGS
mv JZ6W-ntuples/*.root $OUTDIR/
rm -rf JZ6W/ JZ6W-ntuples/

# Gammatautau
mkdir Gammatautau-ntuples
RunNtupleCreator.py $MXAOD_DIR "*Gammatautau*" -d Gammatautau \
                    -o Gammatautau-ntuples/Gammatautau.root --truth $FLAGS
mv Gammatautau-ntuples/*.root $OUTDIR/
rm -rf Gammatautau/ Gammatautau-ntuples
