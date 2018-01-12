#!/usr/bin/env bash
set -e

NTUPLE_DIR="ntuples_v12/"
OUTDIR="hdf_v12/"

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


# TRAINING

# 1-prong signal (training)
echo "Converting 1-prong signal sample (train)..."
ntuple2hdf.py $OUTDIR/sig1P_v12_train_%d.h5 truth1p \
    $NTUPLE_DIR/*Gammatautau*.root \
    $FLAGS --sel "$TRAIN_SEL"

# 3-prong signal (training)
echo "Converting 3-prong signal sample (train)..."
ntuple2hdf.py $OUTDIR/sig3P_v12_train_%d.h5 truth3p \
    $NTUPLE_DIR/*Gammatautau*.root \
    $FLAGS --sel "$TRAIN_SEL"

# 1-prong background (training)
echo "Converting 1-prong background sample (train)..."
ntuple2hdf.py $OUTDIR/bkg1P_v12_train_%d.h5 1p $NTUPLE_DIR/*JZ?W*.root \
    $FLAGS --sel "$TRAIN_SEL"

# 3-prong background (training)
echo "Converting 3-prong background sample (train)..."
ntuple2hdf.py $OUTDIR/bkg3P_v12_train_%d.h5 3p $NTUPLE_DIR/*JZ?W*.root \
    $FLAGS --sel "$TRAIN_SEL"


# TESTING

# 1-prong signal (testing)
echo "Converting 1-prong signal sample (test)..."
ntuple2hdf.py $OUTDIR/sig1P_v12_test_%d.h5 truth1p \
    $NTUPLE_DIR/*Gammatautau*.root \
    $FLAGS --sel "$TEST_SEL"

# 3-prong signal (testing)
echo "Converting 3-prong signal sample (test)..."
ntuple2hdf.py $OUTDIR/sig3P_v12_test_%d.h5 truth3p \
    $NTUPLE_DIR/*Gammatautau*.root \
    $FLAGS --sel "$TEST_SEL"

# 1-prong background (testing)
echo "Converting 1-prong background sample (test)..."
ntuple2hdf.py $OUTDIR/bkg1P_v12_test_%d.h5 1p $NTUPLE_DIR/*JZ?W*.root \
    $FLAGS --sel "$TEST_SEL"

# 3-prong background (testing)
echo "Converting 3-prong background sample (test)..."
ntuple2hdf.py $OUTDIR/bkg3P_v12_test_%d.h5 3p $NTUPLE_DIR/*JZ?W*.root \
    $FLAGS --sel "$TEST_SEL"
