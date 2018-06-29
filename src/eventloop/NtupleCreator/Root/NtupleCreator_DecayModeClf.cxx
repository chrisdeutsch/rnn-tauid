#include "TFile.h"

#include "AsgTools/MessageCheck.h"
#include "EventLoop/Job.h"
#include "EventLoop/StatusCode.h"
#include "EventLoop/Worker.h"

#include "NtupleCreator/NtupleCreator_DecayModeClf.h"

#include "xAODEventInfo/EventInfo.h"
#include "xAODTau/TauJetContainer.h"

// this is needed to distribute the algorithm to the workers
ClassImp(NtupleCreator_DecayModeClf)


NtupleCreator_DecayModeClf::NtupleCreator_DecayModeClf()
{
}

EL::StatusCode NtupleCreator_DecayModeClf::setupJob(EL::Job& job)
{
    job.useXAOD();
    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::histInitialize()
{
    TFile *outputFile = TFile::Open(m_outputName.c_str(), "RECREATE");
    m_tree = new TTree("tree", "flat tree");
    m_tree->SetDirectory(outputFile);
    m_tree->SetMaxTreeSize(8000000000);
    m_tree->SetAutoSave(0);

    // Set output branches
    m_tree->Branch("TauJets.mcEventNumber", &m_mcEventNumber);
    m_tree->Branch("TauJets.mcEventWeight", &m_mcEventWeight);
    m_tree->Branch("TauJets.nTracks", &m_nTracks);
    m_tree->Branch("TauJets.pt", &m_pt);
    m_tree->Branch("TauJets.eta", &m_eta);
    m_tree->Branch("TauJets.phi", &m_phi);
    m_tree->Branch("TauJets.BDTJetScore", &m_BDTJetScore);

    // Reco Decay mode?

    // Truth variables
    if (m_deco_truth) {
        m_tree->Branch("TauJets.truthProng", &m_truthProng,
                       "TauJets.truthProng/l");
        m_tree->Branch("TauJets.truthEtaVis", &m_truthEtaVis);
        m_tree->Branch("TauJets.truthPtVis", &m_truthPtVis);
        m_tree->Branch("TauJets.IsTruthMatched", &m_IsTruthMatched);
        m_tree->Branch("TauJets.truthDecayMode", &m_truthDecayMode,
                       "TauJets.truthDecayMode/l");
    }

    // Variables for regular ID
    m_tree->Branch("TauJets.mu", &m_mu);
    m_tree->Branch("TauJets.nVtxPU", &m_nVtxPU);

    // TauJet variables
    m_tree->Branch("TauJets.jet_Pt", &m_jet_Pt);
    m_tree->Branch("TauJets.jet_Phi", &m_jet_Phi);
    m_tree->Branch("TauJets.jet_Eta", &m_jet_Eta);

    // Charged PFO variables
    m_tree->Branch("ChargedPFO.pt", &m_pfo_chargedPt);
    m_tree->Branch("ChargedPFO.phi", &m_pfo_chargedPhi);
    m_tree->Branch("ChargedPFO.eta", &m_pfo_chargedEta);

    // Neutral PFO variables
    m_tree->Branch("NeutralPFO.pt", &m_pfo_neutralPt);
    m_tree->Branch("NeutralPFO.phi", &m_pfo_neutralPhi);
    m_tree->Branch("NeutralPFO.eta", &m_pfo_neutralEta);
    m_tree->Branch("NeutralPFO.pi0BDT", &m_pfo_neutralPi0BDT);
    m_tree->Branch("NeutralPFO.ptSub", &m_pfo_neutralPtSub);
    m_tree->Branch("NeutralPFO.nHitsInEM1", &m_pfo_neutralNHitsInEM1);
    m_tree->Branch("NeutralPFO.SECOND_R", &m_pfo_neutral_SECOND_R);
    m_tree->Branch("NeutralPFO.SECOND_LAMBDA", &m_pfo_neutral_SECOND_LAMBDA);
    m_tree->Branch("NeutralPFO.CENTER_LAMBDA", &m_pfo_neutral_CENTER_LAMBDA);
    m_tree->Branch("NeutralPFO.ENG_FRAC_MAX", &m_pfo_neutral_ENG_FRAC_MAX);
    m_tree->Branch("NeutralPFO.ENG_FRAC_CORE", &m_pfo_neutral_ENG_FRAC_CORE);
    m_tree->Branch("NeutralPFO.SECOND_ENG_DENS", &m_pfo_neutral_SECOND_ENG_DENS);
    m_tree->Branch("NeutralPFO.nPosECells_EM1", &m_pfo_neutral_NPosECells_EM1);
    m_tree->Branch("NeutralPFO.nPosECells_EM2", &m_pfo_neutral_NPosECells_EM2);
    m_tree->Branch("NeutralPFO.secondEtaWRTClusterPosition_EM1",
                   &m_pfo_neutral_secondEtaWRTClusterPosition_EM1);
    m_tree->Branch("NeutralPFO.secondEtaWRTClusterPosition_EM2",
                   &m_pfo_neutral_secondEtaWRTClusterPosition_EM2);
    m_tree->Branch("NeutralPFO.energyfrac_EM1", &m_pfo_neutral_energyfrac_EM1);
    m_tree->Branch("NeutralPFO.energyfrac_EM2", &m_pfo_neutral_energyfrac_EM2);

    // Shot PFO variables
    m_tree->Branch("ShotPFO.pt", &m_pfo_shotPt);
    m_tree->Branch("ShotPFO.phi", &m_pfo_shotPhi);
    m_tree->Branch("ShotPFO.eta", &m_pfo_shotEta);

    // Conversion track variables
    m_tree->Branch("ConvTrack.pt", &m_conv_pt);
    m_tree->Branch("ConvTrack.phi", &m_conv_phi);
    m_tree->Branch("ConvTrack.eta", &m_conv_eta);

    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::fileExecute ()
{
    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::changeInput(bool /*firstFile*/)
{
    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::initialize()
{
    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::execute()
{
    ANA_CHECK_SET_TYPE(EL::StatusCode);

    // EventInfo
    const xAOD::EventInfo *eventInfo = nullptr;
    ANA_CHECK(evtStore()->retrieve(eventInfo, "EventInfo"));
    m_mcEventNumber = eventInfo->mcEventNumber();
    m_mcEventWeight = eventInfo->mcEventWeight();

    const xAOD::TauJetContainer *taus = nullptr;
    ANA_CHECK(evtStore()->retrieve(taus, "TauJets"));

    for (auto tau : *taus) {
        m_nTracks = tau->auxdata<int>("nTracks");
        m_pt = tau->pt();
        m_eta = tau->eta();
        m_phi = tau->phi();
        m_BDTJetScore = tau->discriminant(xAOD::TauJetParameters::TauID::
                                          BDTJetScore);
        m_BDTJetScoreSigTrans = tau->discriminant(xAOD::TauJetParameters::TauID::
                                                  BDTJetScoreSigTrans);

        // Truth variables
        if (m_deco_truth) {
            m_truthProng = tau->auxdata<unsigned long>("truthProng");
            m_truthEtaVis = tau->auxdata<double>("truthEtaVis");
            m_truthPtVis = tau->auxdata<double>("truthPtVis");
            m_IsTruthMatched = tau->auxdata<char>("IsTruthMatched");
            m_truthDecayMode = tau->auxdata<unsigned long>("truthDecayMode");
        }

        // Variables for regular ID
        m_mu = tau->auxdata<double>("mu");
        m_nVtxPU = tau->auxdata<int>("nVtxPU");

        // TauJet variables
        m_jet_Pt = tau->auxdata<float>("jet_Pt");
        m_jet_Phi = tau->auxdata<float>("jet_Phi");
        m_jet_Eta = tau->auxdata<float>("jet_Eta");

        // Charged PFO variables
        m_pfo_chargedPt = tau->auxdata<vfloat>("pfo_chargedPt");
        m_pfo_chargedPhi = tau->auxdata<vfloat>("pfo_chargedPhi");
        m_pfo_chargedEta = tau->auxdata<vfloat>("pfo_chargedEta");

        // Neutral PFO variables
        m_pfo_neutralPt = tau->auxdata<vfloat>("pfo_neutralPt");
        m_pfo_neutralPhi = tau->auxdata<vfloat>("pfo_neutralPhi");
        m_pfo_neutralEta = tau->auxdata<vfloat>("pfo_neutralEta");
        m_pfo_neutralPi0BDT = tau->auxdata<vfloat>("pfo_neutralPi0BDT");
        m_pfo_neutralPtSub = tau->auxdata<vfloat>("pfo_neutralPtSub");
        m_pfo_neutralNHitsInEM1 = tau->auxdata<vuint8>("pfo_neutralNHitsInEM1");
        m_pfo_neutral_SECOND_R = tau->auxdata<vfloat>("pfo_neutral_SECOND_R");
        m_pfo_neutral_SECOND_LAMBDA = tau->auxdata<vfloat>("pfo_neutral_SECOND_LAMBDA");
        m_pfo_neutral_CENTER_LAMBDA = tau->auxdata<vfloat>("pfo_neutral_CENTER_LAMBDA");
        m_pfo_neutral_ENG_FRAC_MAX = tau->auxdata<vfloat>("pfo_neutral_ENG_FRAC_MAX");
        m_pfo_neutral_ENG_FRAC_CORE = tau->auxdata<vfloat>("pfo_neutral_ENG_FRAC_CORE");
        m_pfo_neutral_SECOND_ENG_DENS = tau->auxdata<vfloat>("pfo_neutral_SECOND_ENG_DENS");
        m_pfo_neutral_NPosECells_EM1 = tau->auxdata<vint>("pfo_neutral_NPosECells_EM1");
        m_pfo_neutral_NPosECells_EM2 = tau->auxdata<vint>("pfo_neutral_NPosECells_EM2");
        m_pfo_neutral_secondEtaWRTClusterPosition_EM1 =
          tau->auxdata<vfloat>("pfo_neutral_secondEtaWRTClusterPosition_EM1");
        m_pfo_neutral_secondEtaWRTClusterPosition_EM2 =
          tau->auxdata<vfloat>("pfo_neutral_secondEtaWRTClusterPosition_EM2");
        m_pfo_neutral_energyfrac_EM1 = tau->auxdata<vfloat>("pfo_neutral_energyfrac_EM1");
        m_pfo_neutral_energyfrac_EM2 = tau->auxdata<vfloat>("pfo_neutral_energyfrac_EM2");

        // Shot PFO variables
        m_pfo_shotPt = tau->auxdata<vfloat>("pfo_shotPt");
        m_pfo_shotPhi = tau->auxdata<vfloat>("pfo_shotPhi");
        m_pfo_shotEta = tau->auxdata<vfloat>("pfo_shotEta");

        // Conversion track variables
        m_conv_pt = tau->auxdata<vfloat>("conv_pt");
        m_conv_phi = tau->auxdata<vfloat>("conv_phi");
        m_conv_eta = tau->auxdata<vfloat>("conv_eta");

        // Fill that puppy
        m_tree->Fill();
    }

    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::postExecute()
{
    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::finalize()
{
    return EL::StatusCode::SUCCESS;
}

EL::StatusCode NtupleCreator_DecayModeClf::histFinalize()
{
    auto file = m_tree->GetCurrentFile();
    file->Write();
    file->Close();
    return EL::StatusCode::SUCCESS;
}
