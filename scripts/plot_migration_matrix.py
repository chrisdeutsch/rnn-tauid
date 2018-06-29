#!/usr/bin/env python
import argparse
from itertools import product

import numpy as np
import h5py
from sklearn.metrics import confusion_matrix

import matplotlib as mpl
mpl.use("PDF")
from rnn_tauid.plotting.mpl_style import mpl_setup
mpl_setup(scale=0.48, aspect_ratio=8.0 / 6.0, pad_left=0.20, pad_right=1.0)
mpl.rcParams["xtick.labelsize"] = 7
mpl.rcParams["ytick.labelsize"] = 7
mpl.rcParams["xtick.major.size"] = 4
mpl.rcParams["ytick.major.size"] = 4

import matplotlib.pyplot as plt


def migration_matrix(truth, reco, comp=False):
    assert len(truth) == len(reco)
    diag_eff = np.count_nonzero(truth == reco) / float(len(truth))

    cm = confusion_matrix(truth, reco).T[::-1]

    # Normalize columns (migration matrix) or rows (composition matrix)
    if comp:
        axis = 1
    else:
        axis = 0

    cm_norm = 100 * np.true_divide(cm, np.sum(cm, axis=axis, keepdims=True))

    return diag_eff, cm_norm


def main(args):
    with h5py.File(args.data, "r", driver="family", memb_size=8*1024**3) as f:
        nTracks = f["TauJets/nTracks"][...]
        mask = (nTracks == 1) | (nTracks == 3)

        if args.tauid_medium:
            bdtscore = f["TauJets/BDTJetScoreSigTrans"][...]
            cut_1p = 1.0 - 0.75
            cut_3p = 1.0 - 0.6
            mask = ((nTracks == 1) & (bdtscore > cut_1p)) | ((nTracks == 3) & (bdtscore > cut_3p))

        truth = f["TauJets/truthDecayMode"][...]

        # Mask out training set
        #idx = int(0.5 * len(truth))
        #mask[:idx] = False

        #truth = truth[mask]

        if args.pt:
            pt = f["TauJets/pt"][...]
            pt_low = 1000 * min(args.pt)
            pt_high = 1000 * max(args.pt)
            pt_sel = (pt_low < pt) & (pt < pt_high)
            pt_sel = pt_sel[mask]

            truth = truth[pt_sel]

    with h5py.File(args.deco, "r") as f:
        reco = f["score"][...]

        # Set probabilities to zero
        if args.use_ntracks:
            oneprong = nTracks == 1
            threeprong = ~oneprong
            reco[oneprong, 3:] = 0
            reco[threeprong, :3] = 0

        reco = np.argmax(reco, axis=1)
        reco = reco[mask]

        if args.pt:
            reco = reco[pt_sel]

    diag_eff, cm = migration_matrix(truth, reco, comp=args.composition)

    np.set_printoptions(suppress=True)
    print(cm)

    fig, ax = plt.subplots()
    ax.imshow(cm, vmin=0, vmax=100, cmap="Blues")

    # ticklabels = ["1p0n", "1p1n", "1pXn", "3p0n", "3pXn"]
    ticklabels = [r"$h^\pm$", r"$h^\pm \pi^0$", r"$h^\pm \geq 2 \pi^0$",
                  r"$3 h^\pm$", r"$3 h^\pm \geq 1 \pi^0$"]

    ax.minorticks_off()
    ax.set_xticks(np.arange(cm.shape[0]))
    ax.set_xticklabels(ticklabels)
    ax.get_xaxis().set_ticks_position("bottom")
    ax.set_yticks(np.arange(cm.shape[0]))
    ax.set_yticklabels(ticklabels[::-1])
    ax.get_yaxis().set_ticks_position("left")

    ax.set_xlabel("True decay mode", ha="right", x=1.0)
    ax.set_ylabel("Reconstructed decay mode", ha="right", y=1.0)

    # Set values on plot
    for i, j in product(range(cm.shape[0]), range(cm.shape[0])):
        ax.text(i, j, "{:.1f}".format(np.round(cm[j,i], decimals=1)+0),
                ha="center", va="center", fontsize=7)

    ax.set_ylim(4.5, -1.5)
    ax.set_aspect(0.7)

    ax.text(4.35, -1, "Diagonal efficiency:\n{:.1f}%".format(100 * diag_eff),
            ha="right", va="center")

    if args.composition:
        norm_label = "Row\nnorm."
    else:
        norm_label = "Column\nnorm."

    ax.text(-0.35, -1, norm_label, va="center")

    fig.savefig(args.out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("deco")
    parser.add_argument("out")
    parser.add_argument("--composition", action="store_true")
    parser.add_argument("--pt", nargs=2, type=float)
    parser.add_argument("--tauid-medium", action="store_true", help="1P eff. 75%%, 3P eff. 60%%")
    parser.add_argument("--use-ntracks", action="store_true")

    args = parser.parse_args()
    main(args)
