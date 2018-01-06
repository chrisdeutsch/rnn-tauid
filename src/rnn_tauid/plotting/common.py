from collections import Iterable

import h5py
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve

from rnn_tauid.plotting.mpl_style import mpl_setup
from rnn_tauid.plotting.base import Plot
from rnn_tauid.plotting.utils import colors
from rnn_tauid.preprocessing import pt_reweight

mpl_setup()

h5opt = dict(driver="family", memb_size=8*1024**3)


def load_scores(sigf, bkgf):
    with h5py.File(sigf, "r") as s, \
         h5py.File(bkgf, "r") as b:
        sig_score = s["score"][...]
        bkg_score = b["score"][...]

    return sig_score, bkg_score


def load_from_samples(sigf, bkgf, variables):
    sig_dict = dict()
    bkg_dict = dict()

    with h5py.File(sigf, "r", **h5opt) as s, \
         h5py.File(bkgf, "r", **h5opt) as b:

        for v in variables:
            sig_dict[v] = s[v][...]
            bkg_dict[v] = b[v][...]

    return sig_dict, bkg_dict


class HistPlot(Plot):
    def __init__(self, var):
        super(HistPlot, self).__init__()

        if not isinstance(var, Iterable):
            self.var = [var]
        else:
            self.var = var





    def plot(self, samples, scores=None):


        fig, ax = plt.subplots()

        return fig



class ScorePlot(Plot):
    def __init__(self, plot_train=False, plot_test=True, log_y=False, **kwargs):
        super(ScorePlot, self).__init__()

        self.plot_train = plot_train
        self.plot_test = plot_test
        self.log_y = log_y

        kwargs.setdefault("histtype", "step")
        kwargs.setdefault("density", True)
        self.histopt = kwargs


    def plot(self, samples, scores=None):
        fig, ax = plt.subplots()
        self.fig = fig

        if self.plot_train:
            sig_dict, bkg_dict = load_from_samples(
                samples.sig_train, samples.bkg_train, ["TauJets/pt"])
            sig_score, bkg_score = load_scores(scores.sig_train,
                                               scores.bkg_train)
            sig_w, bkg_w = pt_reweight(sig_dict["TauJets/pt"],
                                       bkg_dict["TauJets/pt"])

            ax.hist(sig_score, weights=sig_w, label="Sig (train)",
                    color=c["green"], **self.histopt)
            ax.hist(bkg_score, weights=bkg_w, label="Bkg (train)",
                    color=c["violet"], **self.histopt)

        if self.plot_test:
            sig_dict, bkg_dict = load_from_samples(
                samples.sig_train, samples.bkg_train, ["TauJets/pt"])
            sig_score, bkg_score = load_scores(scores.sig_train,
                                               scores.bkg_train)
            sig_w, bkg_w = pt_reweight(sig_dict["TauJets/pt"],
                                       bkg_dict["TauJets/pt"])

            ax.hist(sig_score, weights=sig_w, label="Sig (test)",
                    color=c["red"], **self.histopt)
            ax.hist(bkg_score, weights=bkg_w, label="Bkg (test)",
                    color=c["blue"], **self.histopt)

        if self.log_y:
            ax.set_yscale("log")

        # Get sensible upper limit for y-axis
        ax.autoscale()
        y_lo, y_hi = ax.get_ylim()

        if self.log_y:
            y_hi *= 1.5
        else:
            diff = y_hi - y_lo
            y_hi += 0.05 * diff

        ax.set_ylim(y_lo, y_hi)

        ax.legend()
        ax.set_xlabel("Signal probability", x=1, ha="right")
        ax.set_ylabel("Norm. number of entries", y=1, ha="right")

        return fig


class ROC(Plot):
    pass


class FlattenerPlot(Plot):
    pass


class EfficiencyPlot(Plot):
    pass


class RatioPlot(Plot):
    pass


class RejectionPlot(Plot):
    pass
