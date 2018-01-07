from collections import namedtuple

import numpy as np
import h5py
from scipy.interpolate import interp1d
from scipy.stats import binned_statistic
from sklearn.metrics import roc_curve


class Sample(object):
    def __init__(self, *args):
        self.files = args
        self.cache = {}


    def get_variables(self, *args, **kwargs):
        store_cache = kwargs.get("cache", True)

        return_vars = {}

        # Requested variables
        variables = set(args)
        # Requested variables that are in cache
        in_cache = set(self.cache.keys()) & variables
        # Requested not in cache
        variables -= in_cache

        # Fill return dict from cache
        for var in in_cache:
            return_vars[var] = self.cache[var]

        # Variables found in input files
        found = set()

        length = None
        for fn in self.files:
            # Set driver to family if "%d" in filename
            h5opt = {}
            if "%d" in fn:
                h5opt["driver"] = "family"
                h5opt["memb_size"] = 8 * 1024**3

            with h5py.File(fn, "r", **h5opt) as f:
                for var in variables:
                    if var in f:
                        # Check that variables have the same length
                        var_len = len(f[var])
                        if length:
                            assert(var_len == length)
                        length = var_len

                        # Load variable
                        return_vars[var] = f[var][...]
                        found.add(var)

                        if store_cache:
                            self.cache[var] = return_vars[var]

        diff = variables - found
        if len(diff) > 0:
            raise RuntimeError("Variables {} not found".format(str(variables)))

        return return_vars


SampleHolder = namedtuple("SampleHolder", ["sig_train", "sig_test",
                                           "bkg_train", "bkg_test"])


colors = {
    "red": "#e41a1c",
    "blue": "#377eb8",
    "green": "#4daf4a",
    "violet": "#984ea3",
    "orange": "#ff7f00",
    "yellow": "#ffff33",
    "brown": "#a65628",
    "pink": "#f781bf",
    "grey": "#999999"
}

colorseq = [
    colors["red"],
    colors["blue"],
    colors["green"],
    colors["violet"],
    colors["orange"],
    colors["yellow"],
    colors["brown"],
    colors["pink"],
    colors["grey"]
]


def roc(y_true, y, **kwargs):
    fpr, tpr, thr = roc_curve(y_true, y, **kwargs)
    nonzero = fpr != 0
    eff, rej = tpr[nonzero], 1.0 / fpr[nonzero]

    return eff, rej


def roc_ratio(y_true, y1, y2, **kwargs):
    eff1, rej1 = roc(y_true, y1, **kwargs)
    eff2, rej2 = roc(y_true, y2, **kwargs)

    roc1 = interp1d(eff1, rej1, copy=False)
    roc2 = interp1d(eff2, rej2, copy=False)

    lower_bound = max(eff1.min(), eff2.min())
    upper_bound = min(eff1.max(), eff2.max())

    eff = np.linspace(lower_bound, upper_bound, 100)
    ratio = roc1(eff) / roc2(eff)

    return eff, ratio


def binned_efficiency_ci(x, pass_sel, weight=None, ci=68.3, nbootstrap=100,
                         return_inverse=False, **kwargs):
    # TODO: Accept multiple pass_sel
    pass_sel = pass_sel.astype(np.float32)

    # Check inputs
    assert len(x) == len(pass_sel)
    if weight:
        assert len(x) == len(weight)

    efficiency = []
    for i in range(nbootstrap):
        idx = np.random.randint(len(x), size=len(x))
        x_bs = x[idx]

        # Weight of passing events
        pass_weight_bs = pass_sel[idx]
        if weight:
            weight_bs = weight[idx]
            pass_weight_bs *= weight_bs

        # Pass selection
        p, _, _ = binned_statistic(x, pass_weight_bs, statistic="sum",
                                      **kwargs)

        # Total
        if weight:
            t, _, _ = binned_statistic(x, weight_bs, statistic="sum",
                                          **kwargs)
        else:
            t, _, _ = binned_statistic(x, pass_weight_bs, statistic="count",
                                          **kwargs)

        efficiency.append(p / t)

    efficiency = np.array(efficiency)

    if return_inverse:
        efficiency = 1.0 / efficiency

    perc_lo = (100.0 - ci) / 2.0
    perc_hi = 100.0 - perc_lo

    ci_lo, ci_hi = np.percentile(efficiency, [perc_lo, perc_hi], axis=0)
    mean = np.mean(efficiency, axis=0)
    median = np.median(efficiency, axis=0)

    efficiency_ci = namedtuple("EfficiencyCI", ["mean", "median", "ci"])
    return efficiency_ci(mean=mean, median=median, ci=(ci_lo, ci_hi))
