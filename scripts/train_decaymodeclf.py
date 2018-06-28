#!/usr/bin/env python
import argparse
import sys
import logging


def main(args):
    import numpy as np
    import h5py

    from keras.optimizers import SGD
    from keras.callbacks import EarlyStopping, ModelCheckpoint, CSVLogger, \
        ReduceLROnPlateau

    from rnn_tauid.models import decaymodeclf_model
    from rnn_tauid.utils import load_vars_decaymodeclf, load_data_decaymodeclf, train_test_split
    from rnn_tauid.preprocessing import preprocess, save_preprocessing

    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("main")

    # Load rules for variables from file or use defaults if None
    log.info("Loading input variable definitions")
    chrg_vars, neut_vars, shot_vars, conv_vars = load_vars_decaymodeclf(var_module=args.var_mod)

    # Get variable names and preprocessing functions
    chrg_varnames, _, chrg_preproc_func = zip(*chrg_vars)
    neut_varnames, _, neut_preproc_func = zip(*neut_vars)
    shot_varnames, _, shot_preproc_func = zip(*shot_vars)
    conv_varnames, _, conv_preproc_func = zip(*conv_vars)

    # Load data
    h5file = dict(driver="family", memb_size=8*1024**3)
    with h5py.File(args.sig, "r", **h5file) as sig:
        lsig = len(sig["TauJets/pt"])

        if args.fraction:
            sig_idx = int(args.fraction * lsig)
        else:
            sig_idx = lsig

        log.info("Loading sample slice [:{}]".format(sig_idx))

        # Load charged pfo data
        log.info("Loading data for {} charged pfos ...".format(args.num_chrg))
        chrg_data = load_data_decaymodeclf(sig, np.s_[:sig_idx], chrg_vars,
                                           args.num_chrg)

        # Load neutral pfo data
        log.info("Loading data for {} neutral pfos ...".format(args.num_neut))
        neut_data = load_data_decaymodeclf(sig, np.s_[:sig_idx], neut_vars,
                                           args.num_neut)

        # Load shot pfo data
        log.info("Loading data for {} shot pfos ...".format(args.num_shot))
        shot_data = load_data_decaymodeclf(sig, np.s_[:sig_idx], shot_vars,
                                           args.num_shot)

        # Load conversion track data
        log.info("Loading data for {} conversion tracks ...".format(args.num_conv))
        conv_data = load_data_decaymodeclf(sig, np.s_[:sig_idx], conv_vars,
                                           args.num_conv)

    # Validation split
    log.info("Performing train-validation split ...")
    chrg_train, chrg_test, neut_train, neut_test, shot_train, shot_test, conv_train, conv_test = \
        train_test_split([chrg_data, neut_data, shot_data, conv_data],
                         test_size=args.test_size)

    # Apply preprocessing functions
    log.info("Applying preprocessing functions ...")
    chrg_preproc = preprocess(chrg_train, chrg_test, chrg_preproc_func)
    neut_preproc = preprocess(neut_train, neut_test, neut_preproc_func)
    shot_preproc = preprocess(shot_train, shot_test, shot_preproc_func)
    conv_preproc = preprocess(conv_train, conv_test, conv_preproc_func)

    preproc_results = [
        (chrg_varnames, chrg_preproc),
        (neut_varnames, neut_preproc),
        (shot_varnames, shot_preproc),
        (conv_varnames, conv_preproc)
    ]

    log.info("=== Preprocessing rules: ===")
    for variables, preprocessing in preproc_results:
        for var, (offset, scale) in zip(variables, preprocessing):
            log.info("== Variable " + var + ": ==")
            log.info("Offsets: " + str(offset))
            log.info("Scales: " + str(scale) + "\n")

    # Save offsets and scales to hdf5 files
    log.info("Saving preprocessing rules to: {}".format(args.preprocessing))
    save_kwargs = dict(
        chrg_preproc=(chrg_varnames, chrg_preproc),
        neut_preproc=(neut_varnames, neut_preproc),
        shot_preproc=(shot_varnames, shot_preproc),
        conv_preproc=(conv_varnames, conv_preproc)
    )
    save_preprocessing(args.preprocessing, **save_kwargs)

    # Setup training
    chrg_shape = chrg_train.x.shape[1:]
    neut_shape = neut_train.x.shape[1:]
    shot_shape = shot_train.x.shape[1:]
    conv_shape = conv_train.x.shape[1:]

    model = decaymodeclf_model(5, chrg_shape, neut_shape, shot_shape, conv_shape)
    model.summary(print_fn=log.info)

    opt = SGD(lr=0.01, momentum=0.9, nesterov=True)
    model.compile(loss="binary_crossentropy", optimizer=opt,
              metrics=["accuracy"])

    # Configure callbacks
    callbacks = []

    early_stopping = EarlyStopping(
        monitor="val_loss", min_delta=0.0001, patience=args.patience, verbose=1)
    callbacks.append(early_stopping)

    model_checkpoint = ModelCheckpoint(
        args.model, monitor="val_loss", save_best_only=True, verbose=1)
    callbacks.append(model_checkpoint)

    if args.csv_log:
        csv_logger = CSVLogger(args.csv_log)
        callbacks.append(csv_logger)

    reduce_lr = ReduceLROnPlateau(patience=4, verbose=1, min_lr=1e-4)
    callbacks.append(reduce_lr)

    # Start training
    hist = model.fit(
        [chrg_train.x, neut_train.x, shot_train.x, conv_train.x],
        chrg_train.y, sample_weight=chrg_train.w,
        validation_data=([chrg_test.x, neut_test.x, shot_test.x, conv_test.x],
                         chrg_test.y, chrg_test.w),
        epochs=args.epochs, batch_size=args.batch_size, callbacks=callbacks,
        verbose=1)

    # Determine best epoch & validation loss
    val_loss, epoch = min(zip(hist.history["val_loss"], hist.epoch))
    print("\nMinimum val_loss {:.5} at epoch {}".format(val_loss, epoch + 1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sig", help="Input signal")

    parser.add_argument("--preprocessing", default="preproc.h5")
    parser.add_argument("--model", default="model.h5")

    parser.add_argument("--fraction", type=float, default=None)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--csv-log", default=None)
    parser.add_argument("--var-mod", default=None)

    parser.add_argument("--num-chrg", type=int, default=3)
    parser.add_argument("--num-neut", type=int, default=10)
    parser.add_argument("--num-shot", type=int, default=6)
    parser.add_argument("--num-conv", type=int, default=4)

    #assert False, "Neutral PFO THRESHOLD???"

    arch = parser.add_argument_group("architecture")
    arch.add_argument("--dense-units-1-1", type=int, default=32)
    arch.add_argument("--dense-units-1-2", type=int, default=32)

    arch.add_argument("--lstm-units-1-1", type=int, default=32)
    arch.add_argument("--lstm-units-1-2", type=int, default=32)

    arch.add_argument("--dense-units-2-1", type=int, default=32)
    arch.add_argument("--dense-units-2-2", type=int, default=32)

    arch.add_argument("--lstm-units-2-1", type=int, default=24)
    arch.add_argument("--lstm-units-2-2", type=int, default=24)


    arch.add_argument("--dense-units-3-1", type=int, default=128)
    arch.add_argument("--dense-units-3-2", type=int, default=128)
    arch.add_argument("--dense-units-3-3", type=int, default= 16)

    arch.add_argument("--merge-dense-units-1", type=int, default=64)
    arch.add_argument("--merge-dense-units-2", type=int, default=32)

    args = parser.parse_args()
    main(args)
