#!/usr/bin/env python
import argparse
import logging as log
import sys

import numpy as np
import h5py
from tqdm import tqdm

from rnn_tauid import cuts


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile",
                        help="Output file")
    parser.add_argument("selection",
                        choices=["truth1p", "1p",
                                 "truth3p", "3p",
                                 "truthXp", "Xp"],
                        help="Selection to apply to the taus")
    parser.add_argument("infiles", nargs="+",
                        help="Input root files with flattened containers")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Disable progress bar")
    parser.add_argument("--treename", default="CollectionTree",
                        help="Name of the input tree")
    parser.add_argument("--sel", help="Additional selection "
                                      "(e.g. TauJets.mcEventNumber % 2 == 0)")
    parser.add_argument("--debug", action="store_true")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tauid", action="store_true")
    group.add_argument("--decaymodeclf", action="store_true")

    parser.add_argument("--tracks", type=int, default=10,
                        help="Number of tracks to store")
    parser.add_argument("--clusters", type=int, default=6,
                        help="Number of clusters to store")

    parser.add_argument("--chrg-pfos", type=int, default=3,
                        help="Number of charged PFOs to store")
    parser.add_argument("--neut-pfos", type=int, default=10,
                        help="Number of neutral PFOs to store")
    parser.add_argument("--shot-pfos", type=int, default=6,
                        help="Number of shot PFOs to store")
    parser.add_argument("--conv-tracks", type=int, default=4,
                        help="Number of conversion tracks to store")

    return parser.parse_args()


# Global config
default_value = 0
seed = 1234567890

# h5py dataset kwargs
h5opt = {
    "compression": "gzip",
    "compression_opts": 9,
    "shuffle": True,
    "fletcher32": True
}


def load_scalar(branches, sel, outf, args):
    # Number of events after selection
    n_events = None

    for br in tqdm(branches, disable=args.quiet):
        data = root2array(args.infiles, treename=args.treename,
                          branches=br, selection=sel)
        data = data.astype(np.float32)

        # Check if same number of events and shuffle
        if n_events:
            assert n_events == len(data)
        else:
            n_events = len(data)

        random_state = np.random.RandomState(seed=seed)
        random_state.shuffle(data)

        outf.create_dataset("{}/{}".format(*br.split(".")), data=data,
                            dtype=np.float32, **h5opt)


def load_sequence(branches, mask_branch, max_len, sel, outf, args):
    # Number of events after selection
    n_events = None

    mask = root2array(
        args.infiles, treename=args.treename,
        branches=(mask_branch, default_value, max_len),
        selection=sel)
    mask = (mask == 0)

    for br in tqdm(branches, disable=args.quiet):
        data = root2array(args.infiles, treename=args.treename,
                          branches=(br, default_value, max_len),
                          selection=sel)
        data = data.astype(np.float32)

        # Set nan
        data[mask] = np.nan

        # Check if same number of events and shuffle
        if n_events:
            assert n_events == len(data)
        else:
            n_events = len(data)

        random_state = np.random.RandomState(seed=seed)
        random_state.shuffle(data)

        outf.create_dataset("{}/{}".format(*br.split(".")),
                            data=data, dtype=np.float32, **h5opt)


if __name__ == "__main__":
    args = get_args()
    log.basicConfig(level=log.DEBUG if args.debug else log.INFO)

    # Load here to avoid root taking over the command line
    from root_numpy import root2array, list_branches

    # Branches to load
    branches = list_branches(args.infiles[0], treename=args.treename)
    jet_branches = [br for br in branches if br.startswith("TauJets")]

    if args.tauid:
        track_branches = [br for br in branches if br.startswith("TauTracks")]
        cluster_branches = [br for br in branches if br.startswith("TauClusters")]
    elif args.decaymodeclf:
        chrg_pfo_branches = [br for br in branches if br.startswith("ChargedPFO")]
        neut_pfo_branches = [br for br in branches if br.startswith("NeutralPFO")]
        shot_pfo_branches = [br for br in branches if br.startswith("ShotPFO")]
        conv_branches = [br for br in branches if br.startswith("ConvTrack")]
    else:
        log.error("Could not determine run mode. Exiting ...")
        sys.exit(1)

    # Tau selection
    sel = cuts.sel_dict[args.selection]
    if args.sel:
        sel = "({}) && ({})".format(sel, args.sel)

    log.info("Applying selection: " + sel)

    with h5py.File(args.outfile, "w", driver="family",
                   memb_size=8*1024**3) as outf:
        log.info("Loading jet branches ...")
        load_scalar(jet_branches, sel, outf, args)

        if args.tauid:
            log.info("Loading track branches ...")
            load_sequence(track_branches, "TauTracks.pt", args.tracks, sel, outf, args)

            log.info("Loading cluster branches ...")
            load_sequence(cluster_branches, "TauClusters.et", args.clusters, sel, outf, args)

        elif args.decaymodeclf:
            log.info("Loading charged PFO branches ...")
            load_sequence(chrg_pfo_branches, "ChargedPFO.pt", args.chrg_pfos, sel, outf, args)

            log.info("Loading neutral PFO branches ...")
            load_sequence(neut_pfo_branches, "NeutralPFO.pt", args.neut_pfos, sel, outf, args)

            log.info("Loading shot PFO branches ...")
            load_sequence(shot_pfo_branches, "ShotPFO.pt", args.shot_pfos, sel, outf, args)

            log.info("Loading conversion track branches ...")
            load_sequence(conv_branches, "ConvTrack.pt", args.conv_tracks, sel, outf, args)

        else:
            log.error("Could not determine run mode. Exiting ...")
            sys.exit(1)

        # All datasets should have the same length
        log.info("Performing consistency checks ...")
        length = None

        def inconsistency_visitor(name, node):
            """Returns 'True' if file is inconsistent and 'None' otherwise"""
            global length
            if isinstance(node, h5py.Dataset):
                # Node is a dataset
                if length:
                    return True if length != len(node) else None
                else:
                    length = len(node)
            else:
                return None

        inconsistent = outf.visititems(inconsistency_visitor)
        if inconsistent:
            log.error("Array lengths inconsistent")
            sys.exit(1)
        else:
            log.info("File passed consistency check")
