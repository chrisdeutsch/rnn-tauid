def and_cuts(cuts):
    """Combines a list of cut expressions with the logical and"""
    parens = ["({0})".format(cut) for cut in cuts]
    return " && ".join(parens)


mode1P3PWithTruth = "(TauJets.nTracks == 1 || TauJets.nTracks == 3) " \
                    "&& (TauJets.truthProng == 1 || TauJets.truthProng == 3)"
mode1P3PNoTruth = "TauJets.nTracks == 1 || TauJets.nTracks == 3"
eta25 = "abs(TauJets.eta) < 2.5"
eta25Truth = "abs(TauJets.truthEtaVis) < 2.5"
pt20 = "TauJets.pt > 20000"
pt20Truth = "TauJets.truthPtVis > 20000"
vetoCrack = "abs(TauJets.eta) < 1.37 || abs(TauJets.eta) > 1.52"
vetoCrackTruth = "abs(TauJets.truthEtaVis) < 1.37 " \
                 "|| abs(TauJets.truthEtaVis) > 1.52"
matched = "TauJets.IsTruthMatched"
mode1P = "TauJets.nTracks == 1"
mode1PTruth = "TauJets.truthProng == 1"
mode3P = "TauJets.nTracks == 3"
mode3PTruth = "TauJets.truthProng == 3"

matchKin = and_cuts([matched, eta25Truth, vetoCrackTruth, pt20Truth])
baseline = and_cuts([eta25, vetoCrack, pt20, matchKin])
baselineNoTruth = and_cuts([eta25, vetoCrack, pt20])

sel_truth_1p = and_cuts([baseline, mode1P3PWithTruth, mode1P])
sel_1p = and_cuts([baselineNoTruth, mode1P3PNoTruth, mode1P])
sel_truth_3p = and_cuts([baseline, mode1P3PWithTruth, mode3P])
sel_3p = and_cuts([baselineNoTruth, mode1P3PNoTruth, mode3P])
