import numpy as np


def scale(arr, mean=True, std=True, per_obj=True):
    offset = np.zeros(arr.shape[1], dtype=np.float32)
    scale = np.ones(arr.shape[1], dtype=np.float32)

    if mean:
        if per_obj:
            np.nanmean(arr, out=offset, axis=0)
        else:
            offset[:] = np.nanmean(arr)
    if std:
        if per_obj:
            np.nanstd(arr, out=scale, axis=0)
        else:
            scale[:] = np.nanstd(arr)

    return offset, scale


def scale_flat(arr, mean=True, std=True):
    offset = np.float32(0)
    scale = np.float32(1)

    if mean:
        offset = np.mean(arr)
    if std:
        scale = np.std(arr)

    return offset, scale


def robust_scale(arr, median=True, interquartile=True,
                 low_perc=25.0, high_perc=75.0):
    offset = np.zeros(arr.shape[1], dtype=np.float32)
    scale = np.ones(arr.shape[1], dtype=np.float32)

    if median:
        np.nanmedian(arr, out=offset, axis=0)
    if interquartile:
        assert high_perc > low_perc
        perc = np.nanpercentile(arr, [high_perc, low_perc], axis=0)
        np.subtract.reduce(perc, out=scale)

    return offset, scale


def max_scale(arr):
    offset = np.zeros(arr.shape[1], dtype=np.float32)
    scale = np.nanmax(arr, axis=0)

    return offset, scale


def min_max_scale(arr, per_obj=True):
    if per_obj:
        offset = np.nanmin(arr, axis=0)
        scale = np.nanmax(arr, axis=0) - offset
    else:
        offset = np.nanmin(arr)
        scale = np.nanmax(arr) - offset
        offset = np.full(arr.shape[1], fill_value=offset, dtype=np.float32)
        scale = np.full(arr.shape[1], fill_value=scale, dtype=np.float32)

    return offset, scale


def constant_scale(arr, offset=0.0, scale=1.0):
    offset = np.full(arr.shape[1], fill_value=offset, dtype=np.float32)
    scale = np.full(arr.shape[1], fill_value=scale, dtype=np.float32)

    return offset, scale


def pt_reweight(sig_pt, bkg_pt):
    # Binning
    bin_edges = np.percentile(bkg_pt, np.linspace(0.0, 100.0, 50))
    bin_edges[0] = 20000.0  # 20 GeV lower limit
    bin_edges[-1] = 10000000.0  # 10000 GeV upper limit

    # Reweighting coefficient
    sig_hist, _ = np.histogram(sig_pt, bins=bin_edges, density=True)
    bkg_hist, _ = np.histogram(bkg_pt, bins=bin_edges, density=True)

    coeff = sig_hist / bkg_hist

    # Apply reweighting
    sig_weight = np.ones_like(sig_pt)
    bkg_weight = coeff[np.digitize(bkg_pt, bin_edges) - 1].astype(np.float32)

    return sig_weight, bkg_weight


def preprocess(train, test, funcs):
    preprocessing = []
    for i, func in enumerate(funcs):
        xi_train = train.x[..., i]
        xi_test = test.x[..., i]

        # Scale & offset from train, apply to test
        if func:
            offset, scale = func(xi_train)
            xi_train -= offset
            xi_train /= scale

            xi_test -= offset
            xi_test /= scale
        else:
            num = xi_train.shape[1]
            offset = np.zeros((num,), dtype=np.float32)
            scale = np.ones((num,), dtype=np.float32)

        preprocessing.append((offset, scale))

        # Replace nan with zero
        xi_train[np.isnan(xi_train)] = 0
        xi_test[np.isnan(xi_test)] = 0

    return preprocessing


def save_preprocessing(filename, variables, preprocessing):
    with h5py.File(filename, "w") as f:
        # Save variable names
        f["variables"] = np.array(variables, "S")

        # Save preprocessing
        for var, (offset, scale) in zip(variables, preprocessing):
            f[var + "/offset"] = offset
            f[var + "/scale"] = scale
