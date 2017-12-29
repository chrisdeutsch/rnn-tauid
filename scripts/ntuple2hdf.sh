#!/usr/bin/env bash
set -e

NTUPLE_DIR="ntuples_v11/"
OUTDIR="hdf_v11/"

TREENAME="tree"

TRAIN_SEL="TauJets.mcEventNumber % 2 == 0"
TEST_SEL="TauJets.mcEventNumber % 2 == 1"

FLAGS="--treename ${TREENAME}"


if [ ! -d "$OUTDIR" ]; then
    echo "Creating output directory: $OUTDIR"
    mkdir $OUTDIR
else
    echo "Using preexisting output directory: $OUTDIR"
    echo "WARNING: will overwrite any samples located in directory"
fi


# 1-prong signal (training)
echo "Converting 1-prong signal sample..."
ntuple2hdf.py $OUTDIR/sig1P_v11_train_%d.h5 truth1p \
    $NTUPLE_DIR/*Gammatautau*.root \
    $FLAGS --sel "$TRAIN_SEL"

# 3-prong signal (training)
echo "Converting 3-prong signal sample..."
ntuple2hdf.py $OUTDIR/sig3P_v11_train_%d.h5 truth3p \
    $NTUPLE_DIR/*Gammatautau*.root \
    $FLAGS --sel "$TRAIN_SEL"

# 1-prong background (training)
echo "Converting 1-prong background sample..."
ntuple2hdf.py $OUTDIR/bkg1P_v11_train_%d.h5 1p $NTUPLE_DIR/*JZ?W*.root \
    $FLAGS --sel "$TRAIN_SEL"

# 3-prong background (training)
echo "Converting 3-prong background sample..."
ntuple2hdf.py $OUTDIR/bkg3P_v11_train_%d.h5 3p $NTUPLE_DIR/*JZ?W*.root \
    $FLAGS --sel "$TRAIN_SEL"
