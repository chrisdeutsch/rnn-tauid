from functools import partial

import numpy as np
from rnn_tauid.preprocessing import scale, scale_flat, robust_scale, \
                                    constant_scale, min_max_scale


# Template for log10(x + epsilon)
def log10_epsilon(datafile, dest, source_sel=None, dest_sel=None, var=None,
                  epsilon=None):
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    if epsilon:
        np.add(dest[dest_sel], epsilon, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])


# Template for log10(abs(x) + epsilon)
def abs_log10_epsilon(datafile, dest, source_sel=None, dest_sel=None, var=None,
                      epsilon=None):
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.abs(dest[dest_sel], out=dest[dest_sel])
    if epsilon:
        np.add(dest[dest_sel], epsilon, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])


def abs_var(datafile, dest, source_sel=None, dest_sel=None, var=None):
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.abs(dest[dest_sel], out=dest[dest_sel])


# Track variables
pt_log = partial(log10_epsilon, var="TauTracks/pt")

d0_abs = partial(abs_var, var="TauTracks/d0")

d0_abs_log = partial(abs_log10_epsilon,  var="TauTracks/d0", epsilon=1e-6)

z0sinThetaTJVA_abs = partial(abs_var, var="TauTracks/z0sinThetaTJVA")

z0sinThetaTJVA_abs_log = partial(abs_log10_epsilon,
                                 var="TauTracks/z0sinThetaTJVA", epsilon=1e-6)


def pt_jetseed_log(datafile, dest, source_sel=None, dest_sel=None):
    pt = datafile["TauJets/ptJetSeed"][source_sel[0]]
    dest[dest_sel] = np.log10(pt[:, np.newaxis])


# Cluster variables
et_log = partial(
    log10_epsilon, var="TauClusters/et")

SECOND_R_log = partial(
    log10_epsilon, var="TauClusters/SECOND_R", epsilon=0.1)

SECOND_LAMBDA_log = partial(
    log10_epsilon, var="TauClusters/SECOND_LAMBDA", epsilon=0.1)

FIRST_ENG_DENS_log = partial(
    log10_epsilon, var="TauClusters/FIRST_ENG_DENS", epsilon=1e-6)

CENTER_LAMBDA_log = partial(
    log10_epsilon, var="TauClusters/CENTER_LAMBDA", epsilon=1e-6)


# ID vars transformations
def centFrac_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/centFrac"].read_direct(dest, source_sel=source_sel,
                                             dest_sel=dest_sel)
    np.minimum(dest[dest_sel], 1.0, out=dest[dest_sel])

def etOverPtLeadTrk_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/etOverPtLeadTrk"].read_direct(dest, source_sel=source_sel,
                                                    dest_sel=dest_sel)
    np.maximum(dest[dest_sel], 0.1, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])

def absipSigLeadTrk_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/absipSigLeadTrk"].read_direct(dest, source_sel=source_sel,
                                                    dest_sel=dest_sel)
    np.minimum(dest[dest_sel], 30.0, out=dest[dest_sel])

def EMPOverTrkSysP_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/EMPOverTrkSysP"].read_direct(dest, source_sel=source_sel,
                                                   dest_sel=dest_sel)
    np.maximum(dest[dest_sel], 1e-3, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])

def ptRatioEflowApprox_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/ptRatioEflowApprox"].read_direct(
        dest, source_sel=source_sel, dest_sel=dest_sel)
    np.minimum(dest[dest_sel], 4.0, out=dest[dest_sel])

def mEflowApprox_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/mEflowApprox"].read_direct(dest, source_sel=source_sel,
                                                 dest_sel=dest_sel)
    np.maximum(dest[dest_sel], 140.0, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])

def ptIntermediateAxis_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/ptIntermediateAxis"].read_direct(
        dest, source_sel=source_sel, dest_sel=dest_sel)
    np.maximum(dest[dest_sel] / 1000.0, 100.0, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])

def trFlightPathSig_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/trFlightPathSig"].read_direct(dest, source_sel=source_sel,
                                                    dest_sel=dest_sel)
    np.maximum(dest[dest_sel], 0.01, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])

def massTrkSys_trans(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/massTrkSys"].read_direct(dest, source_sel=source_sel,
                                               dest_sel=dest_sel)
    np.maximum(dest[dest_sel], 140.0, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])

# Old stuff
def EMPOverTrkSysP_clip_log(datafile, dest, source_sel=None, dest_sel=None):
    datafile["TauJets/EMPOverTrkSysP"].read_direct(dest, source_sel=source_sel,
                                                   dest_sel=dest_sel)
    np.clip(dest[dest_sel], 1e-3, np.inf, out=dest[dest_sel])
    np.log10(dest[dest_sel], out=dest[dest_sel])


# PFO variables
def Eta(datafile, dest, source_sel=None, dest_sel=None, var="TauPFOs/chargedEta"):
    # Hack to set nans
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.multiply(dest[dest_sel], 0, out=dest[dest_sel])

    if "TauJets/Eta" in datafile:
        eta = datafile["TauJets/Eta"]
    elif "TauJets/eta" in datafile:
        eta = datafile["TauJets/eta"]
    else:
        raise KeyError("TauJets/[Ee]ta not found in sample")

    np.add(dest[dest_sel], eta[source_sel[0]][:, np.newaxis], out=dest[dest_sel])


def Phi(datafile, dest, source_sel=None, dest_sel=None, var="TauPFOs/chargedPhi"):
    # Hack to set nans
    datafile[var].read_direct(dest, source_sel=source_sel,
                                                          dest_sel=dest_sel)
    np.multiply(dest[dest_sel], 0, out=dest[dest_sel])

    if "TauJets/Phi" in datafile:
        phi = datafile["TauJets/Phi"]
    elif "TauJets/phi" in datafile:
        phi = datafile["TauJets/phi"]
    else:
        raise KeyError("TauJets/[Pp]hi not found in sample")

    np.add(dest[dest_sel], phi[source_sel[0]][:, np.newaxis], out=dest[dest_sel])


def dEta(datafile, dest, source_sel=None, dest_sel=None,
         var="TauPFOs/chargedEta", refvar="TauJets/Eta"):
    eta_jet = datafile[refvar][source_sel[0]]
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.subtract(dest[dest_sel], eta_jet[:, np.newaxis], out=dest[dest_sel])


def dPhi(datafile, dest, source_sel=None, dest_sel=None,
         var="TauPFOs/chargedPhi", refvar="TauJets/Phi"):
    phi_jet = datafile[refvar][source_sel[0]]
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.subtract(dest[dest_sel], phi_jet[:, np.newaxis], out=dest[dest_sel])
    np.add(dest[dest_sel], np.pi, out=dest[dest_sel])
    np.fmod(dest[dest_sel], 2 * np.pi, out=dest[dest_sel])
    np.subtract(dest[dest_sel], np.pi, out=dest[dest_sel])


def Pt_jet_log(datafile, dest, source_sel=None, dest_sel=None,
               var="TauPFOs/chargedPt", ptvar="TauJets/Pt"):
    # Hack to set nans
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.multiply(dest[dest_sel], 0, out=dest[dest_sel])
    pt = datafile[ptvar]

    np.add(dest[dest_sel], np.log10(pt[source_sel[0]])[:, np.newaxis],
           out=dest[dest_sel])


# For Track & Cluster RNN
track_dEta = partial(dEta, var="TauTracks/eta", refvar="TauJets/eta")
track_dPhi = partial(dPhi, var="TauTracks/phi", refvar="TauJets/phi")
cluster_dEta = partial(dEta, var="TauClusters/eta", refvar="TauJets/eta")
cluster_dPhi = partial(dPhi, var="TauClusters/phi", refvar="TauJets/phi")

# Abs eta
cluster_abs_eta = partial(abs_var, var="TauClusters/eta")

track_vars = [
    ("TauTracks/pt_log", pt_log, partial(scale, per_obj=False)),
    ("TauTracks/pt_jetseed_log",
     partial(Pt_jet_log, var="TauTracks/pt", ptvar="TauJets/ptJetSeed"),
     partial(scale, per_obj=False)),
    ("TauTracks/d0_abs_log", d0_abs_log, partial(scale, per_obj=False)),
    ("TauTracks/z0sinThetaTJVA_abs_log", z0sinThetaTJVA_abs_log,
     partial(scale, per_obj=False)),
    ("TauTracks/dEta", None, partial(constant_scale, scale=0.4)),
    ("TauTracks/dPhi", None, partial(constant_scale, scale=0.4)),
    ("TauTracks/nInnermostPixelHits", None,
     partial(min_max_scale, per_obj=False)),
    ("TauTracks/nPixelHits", None, partial(min_max_scale, per_obj=False)),
    ("TauTracks/nSCTHits", None, partial(min_max_scale, per_obj=False))
]

cluster_vars = [
    ("TauClusters/et_log", et_log, partial(scale, per_obj=False)),
    ("TauClusters/pt_jetseed_log",
     partial(Pt_jet_log, var="TauClusters/et", ptvar="TauJets/ptJetSeed"),
     partial(scale, per_obj=False)),
    ("TauClusters/dEta", None, partial(constant_scale, scale=0.4)),
    ("TauClusters/dPhi", None, partial(constant_scale, scale=0.4)),
    ("TauClusters/SECOND_R", SECOND_R_log, partial(scale, per_obj=False)),
    ("TauClusters/SECOND_LAMBDA", SECOND_LAMBDA_log,
     partial(scale, per_obj=False)),
    ("TauClusters/CENTER_LAMBDA", CENTER_LAMBDA_log,
     partial(scale, per_obj=False))
]

id1p_vars = [
    ("TauJets/centFrac", centFrac_trans, scale_flat),
    ("TauJets/etOverPtLeadTrk", etOverPtLeadTrk_trans, scale_flat),
    ("TauJets/innerTrkAvgDist", None, scale_flat),
    ("TauJets/absipSigLeadTrk", absipSigLeadTrk_trans, scale_flat),
    ("TauJets/SumPtTrkFrac", None, scale_flat),
    ("TauJets/EMPOverTrkSysP", EMPOverTrkSysP_trans, scale_flat),
    ("TauJets/ptRatioEflowApprox", ptRatioEflowApprox_trans, scale_flat),
    ("TauJets/mEflowApprox", mEflowApprox_trans, scale_flat),
    ("TauJets/ptIntermediateAxis", ptIntermediateAxis_trans, scale_flat)
]

id3p_vars = [
    ("TauJets/centFrac", centFrac_trans, scale_flat),
    ("TauJets/etOverPtLeadTrk", etOverPtLeadTrk_trans, scale_flat),
    ("TauJets/dRmax", None, scale_flat),
    ("TauJets/trFlightPathSig", trFlightPathSig_trans, scale_flat),
    ("TauJets/SumPtTrkFrac", None, scale_flat),
    ("TauJets/EMPOverTrkSysP", EMPOverTrkSysP_trans, scale_flat),
    ("TauJets/ptRatioEflowApprox", ptRatioEflowApprox_trans, scale_flat),
    ("TauJets/mEflowApprox", mEflowApprox_trans, scale_flat),
    ("TauJets/ptIntermediateAxis", ptIntermediateAxis_trans, scale_flat),
    ("TauJets/massTrkSys", massTrkSys_trans, scale_flat)
]
