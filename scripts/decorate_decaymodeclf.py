#!/usr/bin/env python
import argparse
import sys
import logging


def main(args):
    import numpy as np
    import h5py
    from tqdm import tqdm
    from keras.models import load_model

    from rnn_tauid.utils import load_vars_decaymodeclf
    from rnn_tauid.preprocessing import load_preprocessing

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")

    # Load rules for variables from file or use defaults if None
    log.info("Loading input variable definitions")
    chrg_vars, neut_vars, shot_vars, conv_vars = load_vars_decaymodeclf(var_module=args.var_mod)

    # Get variable names and preprocessing functions
    chrg_varnames, chrg_func, _ = zip(*chrg_vars)
    neut_varnames, neut_func, _ = zip(*neut_vars)
    shot_varnames, shot_func, _ = zip(*shot_vars)
    conv_varnames, conv_func, _ = zip(*conv_vars)

    # Load preprocessing
    log.info("Loading preprocessing rules ...")
    offset, scale = load_preprocessing(
        args.preprocessing,
        "chrg_preproc", "neut_preproc", "shot_preproc", "conv_preproc")

    # Load model, determine input sizes and check compatibility
    log.info("Loading model {} ...".format(args.model))
    model = load_model(args.model)

    # Sanity check
    assert len(model.input_shape) == 4

    _, n_chrg, n_chrg_vars = model.input_shape[0]
    _, n_neut, n_neut_vars = model.input_shape[1]
    _, n_shot, n_shot_vars = model.input_shape[2]
    _, n_conv, n_conv_vars = model.input_shape[3]
    _, n_classes = model.output_shape

    assert n_chrg_vars == len(chrg_varnames)
    assert n_neut_vars == len(neut_varnames)
    assert n_shot_vars == len(shot_varnames)
    assert n_conv_vars == len(conv_varnames)

    # Load data and decorate
    h5file = dict(driver="family", memb_size=8*1024**3)
    with h5py.File(args.data, "r", **h5file) as data:
        length = len(data["TauJets/pt"])

        chunks = [(i, min(length, i + args.chunksize))
                  for i in range(0, length, args.chunksize)]

        # Arrays to store inputs / outputs
        log.info("Allocating memory for evaluation ...")
        x_chrg = np.empty((args.chunksize, n_chrg, n_chrg_vars), dtype=np.float32)
        x_neut = np.empty((args.chunksize, n_neut, n_neut_vars), dtype=np.float32)
        x_shot = np.empty((args.chunksize, n_shot, n_shot_vars), dtype=np.float32)
        x_conv = np.empty((args.chunksize, n_conv, n_conv_vars), dtype=np.float32)

        pred = np.empty((length, n_classes), dtype=np.float32)

        # Iterate chunks and predict NN output
        log.info("Starting prediction loop ...")
        for start, stop in tqdm(chunks):
            # Slices
            src_chrg = np.s_[start:stop, :n_chrg]
            src_neut = np.s_[start:stop, :n_neut]
            src_shot = np.s_[start:stop, :n_shot]
            src_conv = np.s_[start:stop, :n_conv]

            len_slice = stop - start

            log.debug("Loading and preprocessing charged PFO data ...")
            for i, (varname, func) in enumerate(zip(chrg_varnames, chrg_func)):
                # Destination slice
                dest = np.s_[:len_slice, ..., i]

                # Call function if var is calculated. Otherwise load from file.
                if func:
                    func(data, x_chrg, source_sel=src_chrg, dest_sel=dest)
                else:
                    data[varname].read_direct(x_chrg, source_sel=src_chrg,
                                              dest_sel=dest)

                # Apply offset and scale
                x_chrg[dest] -= offset["chrg_preproc"][varname]
                x_chrg[dest] /= scale["chrg_preproc"][varname]


            log.debug("Loading and preprocessing neutral PFO data ...")
            for i, (varname, func) in enumerate(zip(neut_varnames, neut_func)):
                # Destination slice
                dest = np.s_[:len_slice, ..., i]

                # Call function if var is calculated. Otherwise load from file.
                if func:
                    func(data, x_neut, source_sel=src_neut, dest_sel=dest)
                else:
                    data[varname].read_direct(x_neut, source_sel=src_neut,
                                              dest_sel=dest)

                # Apply offset and scale
                x_neut[dest] -= offset["neut_preproc"][varname]
                x_neut[dest] /= scale["neut_preproc"][varname]


            log.debug("Loading and preprocessing shot PFO data ...")
            for i, (varname, func) in enumerate(zip(shot_varnames, shot_func)):
                # Destination slice
                dest = np.s_[:len_slice, ..., i]

                # Call function if var is calculated. Otherwise load from file.
                if func:
                    func(data, x_shot, source_sel=src_shot, dest_sel=dest)
                else:
                    data[varname].read_direct(x_shot, source_sel=src_shot,
                                              dest_sel=dest)

                # Apply offset and scale
                x_shot[dest] -= offset["shot_preproc"][varname]
                x_shot[dest] /= scale["shot_preproc"][varname]


            log.debug("Loading and preprocessing conversion track data ...")
            for i, (varname, func) in enumerate(zip(conv_varnames, conv_func)):
                # Destination slice
                dest = np.s_[:len_slice, ..., i]

                # Call function if var is calculated. Otherwise load from file.
                if func:
                    func(data, x_conv, source_sel=src_conv, dest_sel=dest)
                else:
                    data[varname].read_direct(x_conv, source_sel=src_conv,
                                              dest_sel=dest)

                # Apply offset and scale
                x_conv[dest] -= offset["conv_preproc"][varname]
                x_conv[dest] /= scale["conv_preproc"][varname]

            # Apply neutral pt cut
            if args.neut_pt_cut:
                pt_col = neut_varnames.index("NeutralPFO/pt_log")
                neut_pfo_pt = x_neut[..., pt_col]

                # Have to apply preprocessing here too
                o = offset["neut_preproc"]["NeutralPFO/pt_log"][0]
                s = scale["neut_preproc"]["NeutralPFO/pt_log"][0]

                pt_fail = neut_pfo_pt < (np.log10(1e3 * args.neut_pt_cut) - o) / s
                x_neut[pt_fail] = np.nan
                del neut_pfo_pt, pt_fail

            # Replace nans
            x_chrg[np.isnan(x_chrg)] = 0
            x_neut[np.isnan(x_neut)] = 0
            x_shot[np.isnan(x_shot)] = 0
            x_conv[np.isnan(x_conv)] = 0

            # Predict
            pred[start:stop] = model.predict(
                [x_chrg[:len_slice], x_neut[:len_slice], x_shot[:len_slice], x_conv[:len_slice]],
                batch_size=1024**2)

        log.info("Saving predictions to {} ...".format(args.outfile))
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

    parser.add_argument("--neut-pt-cut", type=float, default=1.5)

    args = parser.parse_args()
    main(args)
