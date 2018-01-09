from collections import Iterable

import numpy as np
import h5py
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from scipy.stats import binned_statistic_2d

from rnn_tauid.plotting.mpl_style import mpl_setup
from rnn_tauid.plotting.base import Plot
from rnn_tauid.plotting.utils import colors, colorseq, roc, roc_ratio, \
    binned_efficiency_ci

from rnn_tauid.preprocessing import pt_reweight

# For flattening
from rnn_tauid.flattener import Flattener
from rnn_tauid.binnings import pt_bins, mu_bins

mpl_setup()


class ScorePlot(Plot):
    def __init__(self, train=False, test=True, log_y=False, **kwargs):
        super(ScorePlot, self).__init__()

        self.train = train
        self.test = test
        self.log_y = log_y

        kwargs.setdefault("bins", 50)
        kwargs.setdefault("range", (0, 1))
        kwargs.setdefault("density", True)
        kwargs.setdefault("histtype", "step")

        self.histopt = kwargs


    def plot(self, sh):
        # Compute
        if self.train:
            sig_train = sh.sig_train.get_variables("TauJets/pt", "score")
            bkg_train = sh.bkg_train.get_variables("TauJets/pt", "score")
            sig_train_weight, bkg_train_weight = pt_reweight(
                sig_train["TauJets/pt"], bkg_train["TauJets/pt"])

        if self.test:
            sig_test = sh.sig_test.get_variables("TauJets/pt", "score")
            bkg_test = sh.bkg_test.get_variables("TauJets/pt", "score")
            sig_test_weight, bkg_test_weight = pt_reweight(
                sig_test["TauJets/pt"], bkg_test["TauJets/pt"])

        # Plot
        fig, ax = plt.subplots()
        if self.train:
            ax.hist(sig_train["score"], weights=sig_train_weight,
                    color=colors["green"], label="Sig. train", **self.histopt)
            ax.hist(bkg_train["score"], weights=bkg_train_weight,
                    color=colors["violet"], label="Bkg. train", **self.histopt)

        if self.test:
            ax.hist(sig_test["score"], weights=sig_test_weight,
                    color=colors["red"], label="Sig. test", **self.histopt)
            ax.hist(bkg_test["score"], weights=bkg_test_weight,
                    color=colors["blue"], label="Bkg. test", **self.histopt)

        if self.log_y:
            ax.set_yscale("log")

        ax.legend()
        ax.set_xlabel("Signal probability", x=1, ha="right")
        ax.set_ylabel("Norm. number of entries", y=1, ha="right")

        # Set y-range limits
        ax.autoscale()
        y_lo, y_hi = ax.get_ylim()

        if self.log_y:
            y_hi *= 1.4
            y_lo /= 1.4
        else:
            diff = y_hi - y_lo
            y_hi += 0.05 * diff

        ax.set_ylim(y_lo, y_hi)

        return fig


class ROC(Plot):
    def __init__(self, scores, legend=True, ylim=(1, 1e4)):
        super(ROC, self).__init__()

        if not isinstance(scores, list):
            self.scores = [scores]
        else:
            self.scores = scores

        self.legend = legend
        self.ylim = ylim


    def plot(self, sh):
        sig_test = sh.sig_test.get_variables("TauJets/pt", *self.scores)
        bkg_test = sh.bkg_test.get_variables("TauJets/pt", *self.scores)
        sig_test_weight, bkg_test_weight = pt_reweight(
            sig_test["TauJets/pt"], bkg_test["TauJets/pt"])

        y_true = np.concatenate([np.ones_like(sig_test_weight),
                                 np.zeros_like(bkg_test_weight)])
        weights = np.concatenate([sig_test_weight, bkg_test_weight])

        rocs = []
        for s in self.scores:
            y = np.concatenate([sig_test[s], bkg_test[s]])
            eff, rej = roc(y_true, y, sample_weight=weights)
            rocs.append((eff, rej))

        # Plot
        fig, ax = plt.subplots()

        for s, (eff, rej), c in zip(self.scores, rocs, colorseq):
            label = s.split("/")[-1]
            ax.plot(eff, rej, color=c, label=label)

        ax.set_ylim(self.ylim)
        ax.set_yscale("log")
        ax.set_xlabel("Signal efficiency", x=1, ha="right")
        ax.set_ylabel("Background rejection", y=1, ha="right")

        if self.legend:
            ax.legend()

        return fig


class ROCRatio(Plot):
    def __init__(self, ratios, legend=True, ylim=(0.9, 2.5)):
        super(ROCRatio, self).__init__()

        if not isinstance(ratios, list):
            self.ratios = [ratios]
        else:
            self.ratios = ratios

        scores = []
        for num, denom in ratios:
            scores.append(num)
            scores.append(denom)

        self.scores = scores
        self.legend = legend
        self.ylim = ylim


    def plot(self, sh):
        sig_test = sh.sig_test.get_variables("TauJets/pt", *self.scores)
        bkg_test = sh.bkg_test.get_variables("TauJets/pt", *self.scores)
        sig_test_weight, bkg_test_weight = pt_reweight(
            sig_test["TauJets/pt"], bkg_test["TauJets/pt"])

        y_true = np.concatenate([np.ones_like(sig_test_weight),
                                 np.zeros_like(bkg_test_weight)])
        weights = np.concatenate([sig_test_weight, bkg_test_weight])

        ratios = []
        for num, denom in self.ratios:
            y1 = np.concatenate([sig_test[num], bkg_test[num]])
            y2 = np.concatenate([sig_test[denom], bkg_test[denom]])
            eff, ratio = roc_ratio(y_true, y1, y2, sample_weight=weights)
            ratios.append((eff, ratio))

        # Plot
        fig, ax = plt.subplots()

        for (num, denom), (eff, ratio), c in zip(self.ratios, ratios, colorseq):
            num = num.split("/")[-1]
            denom = denom.split("/")[-1]
            label = "{} / {}".format(num, denom)
            ax.plot(eff, ratio, color=c, label=label)

        ax.set_ylim(self.ylim)
        ax.set_xlabel("Signal efficiency", x=1, ha="right")
        ax.set_ylabel("Rejection ratio", y=1, ha="right")

        if self.legend:
            ax.legend()

        return fig


class FlattenerCutmapPlot(Plot):
    def __init__(self, score, eff):
        super(FlattenerCutmapPlot, self).__init__()

        self.score = score
        self.eff = eff


    def plot(self, sh):
        # Flatten on training sample
        sig_train = sh.sig_train.get_variables("TauJets/pt", "TauJets/mu",
                                               self.score)
        flat = Flattener(pt_bins, mu_bins, self.eff)
        flat.fit(sig_train["TauJets/pt"], sig_train["TauJets/mu"],
                 sig_train[self.score])

        # Plot
        fig, ax = plt.subplots()

        xx, yy = np.meshgrid(flat.x_bins, flat.y_bins - 0.5)
        cm = ax.pcolormesh(xx / 1000.0, yy, flat.cutmap.T)

        ax.set_xscale("log")
        ax.set_xlim(20, 2000)
        ax.set_xlabel(r"Reco. tau $p_\mathrm{T}$ / GeV",
                      ha="right", x=1)
        ax.set_ylim(0, 60)
        ax.set_ylabel(r"$\mu$", ha="right", y=1)

        cb = fig.colorbar(cm)
        cb.set_label("Score threshold", ha="right", y=1)

        label = r"$\epsilon_\mathrm{sig}$ = " + "{:.0f} %".format(100 * self.eff)
        ax.text(0.93, 0.85, label, ha="right", va="bottom", fontsize=7,
                transform=ax.transAxes)

        return fig


class FlattenerEfficiencyPlot(Plot):
    def __init__(self, score, eff):
        super(FlattenerEfficiencyPlot, self).__init__()

        self.score = score
        self.eff = eff


    def plot(self, sh):
        # Flatten on training sample
        sig_train = sh.sig_train.get_variables("TauJets/pt", "TauJets/mu",
                                               self.score)
        flat = Flattener(pt_bins, mu_bins, self.eff)
        flat.fit(sig_train["TauJets/pt"], sig_train["TauJets/mu"],
                 sig_train[self.score])

        # Efficiency on testing sample
        sig_test = sh.sig_test.get_variables("TauJets/pt","TauJets/mu",
                                             self.score)
        pass_thr = flat.passes_thr(sig_test["TauJets/pt"],
                                   sig_test["TauJets/mu"],
                                   sig_test[self.score])

        statistic, _, _, _ = binned_statistic_2d(
            sig_test["TauJets/pt"], sig_test["TauJets/mu"], pass_thr,
            statistic=lambda arr: np.count_nonzero(arr) / float(len(arr)),
            bins=[flat.x_bins, flat.y_bins])

        # Plot
        fig, ax = plt.subplots()

        xx, yy = np.meshgrid(flat.x_bins, flat.y_bins - 0.5)
        cm = ax.pcolormesh(xx / 1000.0, yy, statistic.T)

        ax.set_xscale("log")
        ax.set_xlim(20, 2000)
        ax.set_xlabel(r"Reco. tau $p_\mathrm{T}$ / GeV",
                      ha="right", x=1)
        ax.set_ylim(0, 60)
        ax.set_ylabel(r"$\mu$", ha="right", y=1)

        cb = fig.colorbar(cm)
        cb.set_label("Signal efficiency", ha="right", y=1)

        label = r"$\epsilon_\mathrm{sig}$ = " + "{:.0f} %".format(
            100 * self.eff)
        ax.text(0.93, 0.85, label, ha="right", va="bottom", fontsize=7,
                transform=ax.transAxes)

        return fig


class EfficiencyPlot(Plot):
    def __init__(self, scores, eff, xvar, bins=10, scale=1.0, label=None,
                 ylim=None):
        super(EfficiencyPlot, self).__init__()

        if not isinstance(scores, list):
            scores = [scores]

        self.scores = scores

        if label:
            if not isinstance(label, list):
                label = [label]

            assert len(label) == len(scores)
        else:
            label = [s.split("/")[-1] for s in scores]

        self.label = label

        self.eff = eff
        self.xvar = xvar
        self.bins = bins / scale
        self.scale = scale
        self.ylim = ylim


    def plot(self, sh):
        # Flatten on training sample
        sig_train = sh.sig_train.get_variables("TauJets/pt", "TauJets/mu",
                                               *self.scores)

        # Determine flattening on training sample for all scores
        flat_dict = {}
        for s in self.scores:
            flat_dict[s] = Flattener(pt_bins, mu_bins, self.eff)
            flat_dict[s].fit(sig_train["TauJets/pt"], sig_train["TauJets/mu"],
                             sig_train[s])

        # Variables to determine working points on testing sample
        sig_test = sh.sig_test.get_variables("TauJets/pt", "TauJets/mu",
                                             self.xvar, *self.scores)

        # Check which events pass the working point for each score
        pass_thr = []
        for s in self.scores:
            pass_thr.append(flat_dict[s].passes_thr(sig_test["TauJets/pt"],
                                                    sig_test["TauJets/mu"],
                                                    sig_test[s]))

        efficiencies = binned_efficiency_ci(sig_test[self.xvar], pass_thr,
                                            bins=self.bins)

        # Plot
        fig, ax = plt.subplots()

        bin_center = self.scale * (self.bins[1:] + self.bins[:-1]) / 2.0
        bin_half_width = self.scale * (self.bins[1:] - self.bins[:-1]) / 2.0

        for z, (eff, c, label) in enumerate(
                zip(efficiencies, colorseq, self.label)):
            ci_lo, ci_hi = eff.ci
            yerr = np.vstack([eff.median - ci_lo, ci_hi - eff.median])

            ax.errorbar(bin_center, eff.median,
                        xerr=bin_half_width,
                        yerr=yerr,
                        fmt="o", color=c, label=label, zorder=z)

        if self.ylim:
            ax.set_ylim(ylim)
        else:
            y_lo, y_hi = ax.get_ylim()
            d = 0.05 * (y_hi - y_lo)
            ax.set_ylim(y_lo - d, y_hi + d)

        ax.set_xlabel(self.xvar.split("/")[-1], x=1, ha="right")
        ax.set_ylabel("Efficiency", y=1, ha="right")
        ax.legend()

        return fig


class RejectionPlot(Plot):
    def __init__(self, scores, eff, xvar, bins=10, scale=1.0, label=None,
                 ylim=None):
        super(RejectionPlot, self).__init__()

        if not isinstance(scores, list):
            scores = [scores]

        self.scores = scores

        if label:
            if not isinstance(label, list):
                label = [label]

            assert len(label) == len(scores)
        else:
            label = [s.split("/")[-1] for s in scores]

        self.label = label

        self.eff = eff
        self.xvar = xvar
        self.bins = bins / scale
        self.scale = scale
        self.ylim = ylim


    def plot(self, sh):
        # Flatten on training sample
        sig_train = sh.sig_train.get_variables("TauJets/pt", "TauJets/mu",
                                               *self.scores)

        # Determine flattening on training sample for all scores
        flat_dict = {}
        for s in self.scores:
            flat_dict[s] = Flattener(pt_bins, mu_bins, self.eff)
            flat_dict[s].fit(sig_train["TauJets/pt"], sig_train["TauJets/mu"],
                             sig_train[s])

        # Variables to determine working points on testing sample
        sig_test = sh.sig_test.get_variables("TauJets/pt")
        bkg_test = sh.bkg_test.get_variables("TauJets/pt", "TauJets/mu",
                                             self.xvar, *self.scores)

        # Kinematic reweighting
        sig_test_weight, bkg_test_weight = pt_reweight(
            sig_test["TauJets/pt"], bkg_test["TauJets/pt"])

        # Check which events pass the working point for each score
        pass_thr = []
        for s in self.scores:
            pass_thr.append(flat_dict[s].passes_thr(bkg_test["TauJets/pt"],
                                                    bkg_test["TauJets/mu"],
                                                    bkg_test[s]))

        rejections = binned_efficiency_ci(bkg_test[self.xvar], pass_thr,
                                          bins=self.bins, return_inverse=True)

        # Plot
        fig, ax = plt.subplots()

        bin_center = self.scale * (self.bins[1:] + self.bins[:-1]) / 2.0
        bin_half_width = self.scale * (self.bins[1:] - self.bins[:-1]) / 2.0

        for z, (rej, c, label) in enumerate(
                zip(rejections, colorseq, self.label)):
            ci_lo, ci_hi = rej.ci
            yerr = np.vstack([rej.median - ci_lo, ci_hi - rej.median])

            ax.errorbar(bin_center, rej.median,
                        xerr=bin_half_width,
                        yerr=yerr,
                        fmt="o", color=c, label=label, zorder=z)

        if self.ylim:
            ax.set_ylim(ylim)
        else:
            y_lo, y_hi = ax.get_ylim()
            d = 0.05 * (y_hi - y_lo)
            ax.set_ylim(y_lo - d, y_hi + d)

        ax.set_xlabel(self.xvar.split("/")[-1], x=1, ha="right")
        ax.set_ylabel("Rejection", y=1, ha="right")
        ax.legend()

        return fig



class RatioPlot(Plot):
    pass
