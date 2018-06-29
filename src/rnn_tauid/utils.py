import imp

import numpy as np
from collections import namedtuple
from rnn_tauid.preprocessing import pt_reweight
from sklearn.preprocessing import OneHotEncoder


Data = namedtuple("Data", ["x", "y", "w"])


def load_data(sig, bkg, sig_slice, bkg_slice, invars, num=None):
    # pt-reweighting
    sig_pt = sig["TauJets/pt"][sig_slice]
    bkg_pt = bkg["TauJets/pt"][bkg_slice]

    sig_weight, bkg_weight = pt_reweight(sig_pt, bkg_pt)
    w = np.concatenate([sig_weight, bkg_weight])

    sig_len = len(sig_pt)
    bkg_len = len(bkg_pt)

    del sig_pt, bkg_pt
    del sig_weight, bkg_weight

    # Class labels
    y = np.ones(sig_len + bkg_len, dtype=np.float32)
    y[sig_len:] = 0

    # Load variables
    n_vars = len(invars)

    # If number of timesteps given
    if num:
        x = np.empty((sig_len + bkg_len, num, n_vars))

        sig_src = np.s_[sig_slice, :num]
        bkg_src = np.s_[bkg_slice, :num]
    else:
        x = np.empty((sig_len + bkg_len, n_vars))

        sig_src = np.s_[sig_slice]
        bkg_src = np.s_[bkg_slice]

    for i, (varname, func, _) in enumerate(invars):
        sig_dest = np.s_[:sig_len, ..., i]
        bkg_dest = np.s_[sig_len:, ..., i]

        if func:
            func(sig, x, source_sel=sig_src, dest_sel=sig_dest)
            func(bkg, x, source_sel=bkg_src, dest_sel=bkg_dest)
        else:
            sig[varname].read_direct(x, source_sel=sig_src, dest_sel=sig_dest)
            bkg[varname].read_direct(x, source_sel=bkg_src, dest_sel=bkg_dest)

    return Data(x=x, y=y, w=w)


def load_data_decaymodeclf(sig, sig_slice, invars, num=None):
    sig_pt = sig["TauJets/pt"][sig_slice]
    sig_len = len(sig_pt)
    sig_weight = np.ones_like(sig_pt) # TODO: retrieve EventWeight instead
    w = sig_weight

    # Class labels (OneHotEncoded truth decay mode)
    y = sig["TauJets/truthDecayMode"][sig_slice].reshape((-1, 1))
    enc = OneHotEncoder(sparse=False)
    y = enc.fit_transform(y)

    # Load variables
    n_vars = len(invars)

    # If number of timesteps given
    if num:
        x = np.empty((sig_len, num, n_vars))
        sig_src = np.s_[sig_slice, :num]
    else:
        x = np.empty((sig_len, n_vars))
        sig_src = np.s_[sig_slice]
    for i, (varname, func, _) in enumerate(invars):
        sig_dest = np.s_[:sig_len, ..., i]

        if func:
            func(sig, x, source_sel=sig_src, dest_sel=sig_dest)
        else:
            sig[varname].read_direct(x, source_sel=sig_src, dest_sel=sig_dest)

    return Data(x=x, y=y, w=w)



def parallel_shuffle(sequences):
    size = None
    for seq in sequences:
        if size:
            assert size == len(seq)
        size = len(seq)

        random_state = np.random.RandomState(seed=1234567890)
        random_state.shuffle(seq)


def train_test_split(data, test_size=0.2):
    if not isinstance(data, list):
        data = [data]

    assert len(data) >= 1

    train_size = 1.0 - test_size
    test_start, test_stop = int(train_size * len(data[0].y)), len(data[0].y)

    train = slice(0, test_start)
    test = slice(test_start, test_stop)

    arr = []
    for d in data:
        arr.extend([d.x, d.y, d.w])

    parallel_shuffle(arr)

    ret = []
    for d in data:
        ret.extend([Data(x=d.x[train], y=d.y[train], w=d.w[train]),
                    Data(x=d.x[test], y=d.y[test], w=d.w[test])])
    return ret


def load_vars(var_module=None, tag=None):
    jet_vars = None
    trk_vars = None
    cls_vars = None

    # Load variables from module
    if var_module:
        mod = imp.load_source("var_module", var_module)
        if hasattr(mod, "jet_vars"):
            jet_vars = mod.jet_vars
        if hasattr(mod, "trk_vars"):
            trk_vars = mod.trk_vars
        if hasattr(mod, "cls_vars"):
            cls_vars = mod.cls_vars

    # If still 'None' load defaults
    if not jet_vars:
        if tag == "1p":
            from rnn_tauid.variables import id1p_vars as jet_vars
        elif tag == "3p":
            from rnn_tauid.variables import id3p_vars as jet_vars
        else:
            raise RuntimeError("Unknown prongness")

    if not trk_vars:
        from rnn_tauid.variables import track_vars as trk_vars

    if not cls_vars:
        from rnn_tauid.variables import cluster_vars as cls_vars

    return jet_vars, trk_vars, cls_vars


def load_vars_decaymodeclf(var_module=None, tag=None):
    chrg_pfo_vars = None
    neut_pfo_vars = None
    shot_pfo_vars = None
    conv_vars = None

    # Load variables from module
    if var_module:
        mod = imp.load_source("var_module", var_module)
        if hasattr(mod, "chrg_pfo_vars"):
            chrg_pfo_vars = mod.chrg_pfo_vars
        if hasattr(mod, "neut_pfo_vars"):
            neut_pfo_vars = mod.neut_pfo_vars
        if hasattr(mod, "shot_pfo_vars"):
            shot_pfo_vars = mod.shot_pfo_vars
        if hasattr(mod, "conv_vars"):
            conv_vars = mod.conv_vars

    # If still 'None' load defaults
    if chrg_pfo_vars is None:
        from rnn_tauid.variables import charged_pfo_vars as chrg_pfo_vars

    if neut_pfo_vars is None:
        from rnn_tauid.variables import neutral_pfo_vars as neut_pfo_vars

    if shot_pfo_vars is None:
        from rnn_tauid.variables import shot_vars as shot_pfo_vars

    if conv_vars is None:
        from rnn_tauid.variables import conversion_vars as conv_vars

    return chrg_pfo_vars, neut_pfo_vars, shot_pfo_vars, conv_vars
