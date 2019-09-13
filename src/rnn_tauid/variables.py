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

# ===== TAU IDENTIFICATION =====

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
    np.minimum(dest[dest_sel] / 1000.0, 100.0, out=dest[dest_sel])
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
def Eta(datafile, dest, source_sel=None, dest_sel=None, var="ChargedPFO/eta"):
    # Hack to set nans
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.multiply(dest[dest_sel], 0, out=dest[dest_sel])
    eta = datafile["TauJets/jet_Eta"]
    np.add(dest[dest_sel], eta[source_sel[0]][:, np.newaxis], out=dest[dest_sel])


def Phi(datafile, dest, source_sel=None, dest_sel=None, var="ChargedPFO/phi"):
    # Hack to set nans
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.multiply(dest[dest_sel], 0, out=dest[dest_sel])
    phi = datafile["TauJets/jet_Phi"]
    np.add(dest[dest_sel], phi[source_sel[0]][:, np.newaxis], out=dest[dest_sel])


def dEta(datafile, dest, source_sel=None, dest_sel=None,
         var="ChargedPFO/eta", refvar="TauJets/jet_Eta"):
    eta_jet = datafile[refvar][source_sel[0]]
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.subtract(dest[dest_sel], eta_jet[:, np.newaxis], out=dest[dest_sel])


def dPhi(datafile, dest, source_sel=None, dest_sel=None,
         var="ChargedPFO/phi", refvar="TauJets/jet_Phi"):
    phi_jet = datafile[refvar][source_sel[0]]
    datafile[var].read_direct(dest, source_sel=source_sel, dest_sel=dest_sel)
    np.subtract(dest[dest_sel], phi_jet[:, np.newaxis], out=dest[dest_sel])
    np.add(dest[dest_sel], np.pi, out=dest[dest_sel])
    np.fmod(dest[dest_sel], 2 * np.pi, out=dest[dest_sel])
    np.subtract(dest[dest_sel], np.pi, out=dest[dest_sel])


def Pt_jet_log(datafile, dest, source_sel=None, dest_sel=None,
               var="TauPFOs/chargedPt", ptvar="TauJets/jet_Pt"):
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
    ("TauJets/dRmax", None, scale_flat),
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

# ===== DECAY MODE CLASSIFICATION =====

# Charged PFO
charged_Phi = partial(Phi, var="ChargedPFO/phi")
charged_dPhi = partial(dPhi, var="ChargedPFO/phi")
charged_Eta = partial(Eta, var="ChargedPFO/eta")
charged_dEta = partial(dEta, var="ChargedPFO/eta")
charged_Pt_log = partial(log10_epsilon, var="ChargedPFO/pt")
charged_Pt_jet_log = partial(Pt_jet_log, var="ChargedPFO/pt")

# Neutral PFO
neutral_Phi = partial(Phi, var="NeutralPFO/phi")
neutral_dPhi = partial(dPhi, var="NeutralPFO/phi")
neutral_Eta = partial(Eta, var="NeutralPFO/eta")
neutral_dEta = partial(dEta, var="NeutralPFO/eta")
neutral_Pt_log = partial(log10_epsilon, var="NeutralPFO/pt")
neutral_Pt_jet_log = partial(Pt_jet_log, var="NeutralPFO/pt")
neutral_SECOND_R_log = partial(log10_epsilon, var="NeutralPFO/SECOND_R", epsilon=1)
neutral_secondEtaWRTClusterPosition_EM1_log = partial(
    log10_epsilon, var="NeutralPFO/secondEtaWRTClusterPosition_EM1", epsilon=1e-6)

def PtSubRatio(datafile, dest, source_sel=None, dest_sel=None):
    datafile["NeutralPFO/ptSub"].read_direct(dest, source_sel=source_sel,
                                             dest_sel=dest_sel)
    denom = datafile["NeutralPFO/pt"][source_sel]
    np.add(dest[dest_sel], denom, out=denom)
    np.divide(dest[dest_sel], denom, out=dest[dest_sel])

# Shots
shot_Phi = partial(Phi, var="ShotPFO/phi")
shot_dPhi = partial(dPhi, var="ShotPFO/phi")
shot_Eta = partial(Eta, var="ShotPFO/eta")
shot_dEta = partial(dEta, var="ShotPFO/eta")
shot_Pt_log = partial(log10_epsilon, var="ShotPFO/pt")
shot_Pt_jet_log = partial(Pt_jet_log, var="ShotPFO/pt")

# Conversion tracks
conv_Phi = partial(Phi, var="ConvTrack/phi")
conv_dPhi = partial(dPhi, var="ConvTrack/phi")
conv_Eta = partial(Eta, var="ConvTrack/eta")
conv_dEta = partial(dEta, var="ConvTrack/eta")
conv_Pt_log = partial(log10_epsilon, var="ConvTrack/pt")
conv_Pt_jet_log = partial(Pt_jet_log, var="ConvTrack/pt")

# Side-note: Phi and Eta in this case is the Phi/Eta of the underlying TauJet
#            and not the one of the PFO (implementation detail)

charged_pfo_vars = [
    ("ChargedPFO/phi", charged_Phi, partial(constant_scale, scale=np.pi)),
    ("ChargedPFO/dphi", None, partial(constant_scale, scale=0.4)),
    ("ChargedPFO/eta", charged_Eta, partial(constant_scale, scale=2.5)),
    ("ChargedPFO/deta", None, partial(constant_scale, scale=0.4)),
    ("ChargedPFO/pt_log", charged_Pt_log, partial(scale, per_obj=False)),
    ("ChargedPFO/pt_jet_log", charged_Pt_jet_log, partial(scale, per_obj=False))
]

neutral_pfo_vars = [
    ("NeutralPFO/phi", neutral_Phi, partial(constant_scale, scale=np.pi)),
    ("NeutralPFO/dphi", None, partial(constant_scale, scale=0.4)),
    ("NeutralPFO/eta", neutral_Eta, partial(constant_scale, scale=2.5)),
    ("NeutralPFO/deta", None, partial(constant_scale, scale=0.4)),
    ("NeutralPFO/pt_log", neutral_Pt_log, partial(scale, per_obj=False)),
    ("NeutralPFO/pt_jet_log", neutral_Pt_jet_log, partial(scale, per_obj=False)),

    ("NeutralPFO/pi0BDT", None, None),
    ("NeutralPFO/nHitsInEM1", None, None),
    ("NeutralPFO/SECOND_R", neutral_SECOND_R_log,
     partial(scale, per_obj=False)),
    ("NeutralPFO/secondEtaWRTClusterPosition_EM1",
     neutral_secondEtaWRTClusterPosition_EM1_log,
     partial(scale, per_obj=False)),
    ("NeutralPFO/nPosECells_EM1", None, partial(scale, per_obj=False)),
    ("NeutralPFO/ENG_FRAC_CORE", None, None),
    ("NeutralPFO/energyfrac_EM2", None, None),
    ("NeutralPFO/ptSubRatio", None, None)
]

conversion_vars = [
    ("ConvTrack/phi", conv_Phi, partial(constant_scale, scale=np.pi)),
    ("ConvTrack/dphi", None, partial(constant_scale, scale=0.4)),
    ("ConvTrack/deta", None, partial(constant_scale, scale=0.4)),
    ("ConvTrack/eta", conv_Eta, partial(constant_scale, scale=2.5)),
    ("ConvTrack/pt_log", conv_Pt_log, partial(scale, per_obj=False)),
    ("ConvTrack/pt_jet_log", conv_Pt_jet_log, partial(scale, per_obj=False))
]

shot_vars = [
    ("ShotPFO/phi", shot_Phi, partial(constant_scale, scale=np.pi)),
    ("ShotPFO/dphi", None, partial(constant_scale, scale=0.4)),
    ("ShotPFO/eta", shot_Eta, partial(constant_scale, scale=2.5)),
    ("ShotPFO/deta", None, partial(constant_scale, scale=0.4)),
    ("ShotPFO/pt_log", shot_Pt_log, partial(scale, per_obj=False)),
    ("ShotPFO/pt_jet_log", shot_Pt_jet_log, partial(scale, per_obj=False))
]
