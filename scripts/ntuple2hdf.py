#!/usr/bin/env python
import argparse

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
    parser.add_argument("--tracks", type=int, default=10,
                        help="Number of tracks to store")
    parser.add_argument("--clusters", type=int, default=6,
                        help="Number of clusters to store")
    parser.add_argument("--sel", help="Additional selection "
                                      "(e.g. TauJets.mcEventNumber % 2 == 0)")

    return parser.parse_args()


# Global config
default_value = 0

# h5py dataset kwargs
h5opt = {
    "compression": "gzip",
    "compression_opts": 9,
    "shuffle": True,
    "fletcher32": True
}


if __name__ == "__main__":
    args = get_args()

    # Load here to avoid root taking over the command line
    from root_numpy import root2array, list_branches

    # Branches to load
    branches = list_branches(args.infiles[0], treename=args.treename)
    jet_branches = [br for br in branches if br.startswith("TauJets")]
    track_branches = [br for br in branches if br.startswith("TauTracks")]
    cluster_branches = [br for br in branches if br.startswith("TauClusters")]

    # Tau selection
    sel = cuts.sel_dict[args.selection]
    if args.sel:
        sel = "({}) && ({})".format(sel, args.sel)

    with h5py.File(args.outfile, "w", driver="family",
                   memb_size=8*1024**3) as outf:
        # Number of events after selection
        n_events = None
        seed = 1234567890

        # Jet
        for br in tqdm(jet_branches, desc="Jets", disable=args.quiet):
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

        # Track
        mask = root2array(
            args.infiles, treename=args.treename,
            branches=("TauTracks.pt", default_value, args.tracks),
            selection=sel)
        mask = mask <= 0

        for br in tqdm(track_branches, desc="Tracks", disable=args.quiet):
            data = root2array(args.infiles, treename=args.treename,
                              branches=(br, default_value, args.tracks),
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

        # Cluster
        mask = root2array(
            args.infiles, treename=args.treename,
            branches=("TauClusters.et", default_value, args.clusters),
            selection=sel)
        mask = mask <= 0

        for br in tqdm(cluster_branches, desc="Clusters"):
            data = root2array(args.infiles, treename=args.treename,
                              branches=(br, default_value, args.clusters),
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
