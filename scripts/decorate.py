#!/usr/bin/env python
import argparse
import sys


def main(args):
    import numpy as np
    import h5py
    from tqdm import tqdm
    from keras.models import load_model

    from rnn_tauid.utils import load_vars
    from rnn_tauid.preprocessing import load_preprocessing

    # Determine prongness
    if "1p" in args.data.lower():
        prong = "1p"
    elif "3p" in args.data.lower():
        prong = "3p"
    else:
        print("Could not infer prongness from sample name.")
        sys.exit(1)

    # Load rules for variables from file or use defaults if None
    jet_vars, trk_vars, cls_vars = load_vars(var_module=args.var_mod, tag=prong)

    # Get variable names and preprocessing functions
    jet_varnames, jet_func, _ = zip(*jet_vars)
    trk_varnames, trk_func, _ = zip(*trk_vars)
    cls_varnames, cls_func, _ = zip(*cls_vars)

    # Load preprocessing rules
    if args.do_clusters:
        offset, scale = load_preprocessing(args.preprocessing, "jet_preproc",
                                           "trk_preproc", "cls_preproc")
    else:
        offset, scale = load_preprocessing(args.preprocessing, "jet_preproc",
                                           "trk_preproc")

    # Load model, determine input sizes and check compatibility
    model = load_model(args.model)

    if args.do_clusters:
        assert len(model.input_shape) == 3
    else:
        assert len(model.input_shape) == 2

    if args.do_clusters:
        _, n_trk, n_trk_vars = model.input_shape[0]
        _, n_cls, n_cls_vars = model.input_shape[1]
        _, n_jet_vars = model.input_shape[2]
    else:
        _, n_trk, n_trk_vars = model.input_shape[0]
        _, n_jet_vars = model.input_shape[1]

    assert n_trk_vars == len(trk_varnames)
    assert n_jet_vars == len(jet_varnames)
    if args.do_clusters:
        assert n_cls_vars == len(cls_varnames)

    # Load data and decorate
    h5file = dict(driver="family", memb_size=8*1024**3)
    with h5py.File(args.data, "r", **h5file) as data:
        length = len(data["TauJets/pt"])

        chunks = [(i, min(length, i + args.chunksize))
                  for i in range(0, length, args.chunksize)]

        # Arrays to store inputs / outputs
        x_jet = np.empty((args.chunksize, n_jet_vars), dtype=np.float32)
        x_trk = np.empty((args.chunksize, n_trk, n_trk_vars), dtype=np.float32)
        if args.do_clusters:
            x_cls = np.empty((args.chunksize, n_cls, n_cls_vars), dtype=np.float32)

        pred = np.full(length, -999.0, dtype=np.float32)

        # Iterate chunks and predict NN output
        for start, stop in tqdm(chunks):
            # Slices
            src_jet = np.s_[start:stop]
            src_trk = np.s_[start:stop, :n_trk]
            if args.do_clusters:
                src_cls = np.s_[start:stop, :n_cls]

            len_slice = stop - start

            # Jet variables
            for i, (varname, func) in enumerate(zip(jet_varnames, jet_func)):
                # Destination slice
                dest = np.s_[:len_slice, ..., i]

                # Call function if var is calculated. Otherwise load from file.
                if func:
                    func(data, x_jet, source_sel=src_jet, dest_sel=dest)
                else:
                    data[varname].read_direct(x_jet, source_sel=src_jet, dest_sel=dest)

                # Apply offset and scale
                x_jet[dest] -= offset["jet_preproc"][varname]
                x_jet[dest] /= scale["jet_preproc"][varname]

            # Track variables
            for i, (varname, func) in enumerate(zip(trk_varnames, trk_func)):
                # Destination slice
                dest = np.s_[:len_slice, ..., i]

                # Call function if var is calculated. Otherwise load from file.
                if func:
                    func(data, x_trk, source_sel=src_trk, dest_sel=dest)
                else:
                    data[varname].read_direct(x_trk, source_sel=src_trk,
                                              dest_sel=dest)

                # Apply offset and scale
                x_trk[dest] -= offset["trk_preproc"][varname]
                x_trk[dest] /= scale["trk_preproc"][varname]


            # Cluster variables
            if args.do_clusters:
                for i, (varname, func) in enumerate(zip(cls_varnames,
                                                        cls_func)):
                    # Destination slice
                    dest = np.s_[:len_slice, ..., i]

                    # Call function if var is calculated. Otherwise load from
                    # file.
                    if func:
                        func(data, x_cls, source_sel=src_cls, dest_sel=dest)
                    else:
                        data[varname].read_direct(x_cls, source_sel=src_cls,
                                                  dest_sel=dest)

                    # Apply offset and scale
                    x_cls[dest] -= offset["cls_preproc"][varname]
                    x_cls[dest] /= scale["cls_preproc"][varname]

            # Replace nans
            x_jet[np.isnan(x_jet)] = 0
            x_trk[np.isnan(x_trk)] = 0
            if args.do_clusters:
                x_cls[np.isnan(x_cls)] = 0

            # Predict
            if args.do_clusters:
                pred[start:stop] = model.predict(
                    [x_trk[:len_slice], x_cls[:len_slice], x_jet[:len_slice]],
                    batch_size=1024).ravel()
            else:
                pred[start:stop] = model.predict(
                    [x_trk[:len_slice], x_jet[:len_slice]],
                    batch_size=1024).ravel()


        with h5py.File(args.outfile, "w") as outf:
            outf["score"] = pred


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("preprocessing")
    parser.add_argument("model")
    parser.add_argument("data")

    parser.add_argument("--chunksize", default=500000)
    parser.add_argument("--var-mod", default=None)
    parser.add_argument("-o", "--outfile", default="deco.h5")

    parser.add_argument("--no-clusters", dest="do_clusters",
                        action="store_false")

    args = parser.parse_args()
    main(args)
