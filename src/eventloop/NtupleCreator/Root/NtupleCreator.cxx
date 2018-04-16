#include "TFile.h"

#include "AsgTools/MessageCheck.h"
#include "EventLoop/Job.h"
#include "EventLoop/StatusCode.h"
#include "EventLoop/Worker.h"

#include "NtupleCreator/NtupleCreator.h"

#include "xAODEventInfo/EventInfo.h"
#include "xAODTau/TauJetContainer.h"

// this is needed to distribute the algorithm to the workers
ClassImp(NtupleCreator)


NtupleCreator::NtupleCreator()
{
    // Here you put any code for the base initialization of variables,
    // e.g. initialize all pointers to 0.  Note that you should only put
    // the most basic initialization here, since this method will be
    // called on both the submission and the worker node.  Most of your
    // initialization code will go into histInitialize() and
    // initialize().
}



EL::StatusCode NtupleCreator::setupJob(EL::Job& job)
{
    // Here you put code that sets up the job on the submission object
    // so that it is ready to work with your algorithm, e.g. you can
    // request the D3PDReader service or add output files.  Any code you
    // put here could instead also go into the submission script.  The
    // sole advantage of putting it here is that it gets automatically
    // activated/deactivated when you add/remove the algorithm from your
    // job, which may or may not be of value to you.
    job.useXAOD();
    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::histInitialize()
{
    // Here you do everything that needs to be done at the very
    // beginning on each worker node, e.g. create histograms and output
    // trees.  This method gets called before any input files are
    // connected.
    // TFile *outputFile = wk()->getOutputFile(m_outputName);

    TFile *outputFile = TFile::Open(m_outputName.c_str(), "RECREATE");
    m_tree = new TTree("tree", "flat tree");
    m_tree->SetDirectory(outputFile);
    m_tree->SetMaxTreeSize(8000000000);
    m_tree->SetAutoSave(0);

    // Set output branches
    m_tree->Branch("TauJets.mcEventNumber", &m_mcEventNumber);
    m_tree->Branch("TauJets.nTracks", &m_nTracks);
    m_tree->Branch("TauJets.pt", &m_pt);
    m_tree->Branch("TauJets.eta", &m_eta);
    m_tree->Branch("TauJets.phi", &m_phi);
    m_tree->Branch("TauJets.ptJetSeed", &m_ptJetSeed);
    m_tree->Branch("TauJets.etaJetSeed", &m_etaJetSeed);
    m_tree->Branch("TauJets.phiJetSeed", &m_phiJetSeed);
    m_tree->Branch("TauJets.BDTJetScore", &m_BDTJetScore);

    // RNNJetScore
    if (m_deco_rnnscore) {
        m_tree->Branch("TauJets.RNNJetScore", &m_RNNJetScore);
    }

    // Truth variables
    if (m_deco_truth) {
        m_tree->Branch("TauJets.truthProng", &m_truthProng,
                       "TauJets.truthProng/l");
        m_tree->Branch("TauJets.truthEtaVis", &m_truthEtaVis);
        m_tree->Branch("TauJets.truthPtVis", &m_truthPtVis);
        m_tree->Branch("TauJets.IsTruthMatched", &m_IsTruthMatched);
        m_tree->Branch("TauJets.truthDecayMode", &m_truthDecayMode,
                       "TauJets.truthProng/l");
    }

    // Variables for regular ID
    m_tree->Branch("TauJets.mu", &m_mu);
    m_tree->Branch("TauJets.nVtxPU", &m_nVtxPU);
    m_tree->Branch("TauJets.centFrac", &m_centFrac);
    m_tree->Branch("TauJets.EMPOverTrkSysP", &m_EMPOverTrkSysP);
    m_tree->Branch("TauJets.innerTrkAvgDist", &m_innerTrkAvgDist);
    m_tree->Branch("TauJets.ptRatioEflowApprox", &m_ptRatioEflowApprox);
    m_tree->Branch("TauJets.dRmax", &m_dRmax);
    m_tree->Branch("TauJets.trFlightPathSig", &m_trFlightPathSig);
    m_tree->Branch("TauJets.mEflowApprox", &m_mEflowApprox);
    m_tree->Branch("TauJets.SumPtTrkFrac", &m_SumPtTrkFrac);
    m_tree->Branch("TauJets.absipSigLeadTrk", &m_absipSigLeadTrk);
    m_tree->Branch("TauJets.massTrkSys", &m_massTrkSys);
    m_tree->Branch("TauJets.etOverPtLeadTrk", &m_etOverPtLeadTrk);
    m_tree->Branch("TauJets.ptIntermediateAxis", &m_ptIntermediateAxis);

    // Track variables
    m_tree->Branch("TauTracks.pt", &m_trk_pt);
    m_tree->Branch("TauTracks.eta", &m_trk_eta);
    m_tree->Branch("TauTracks.phi", &m_trk_phi);
    m_tree->Branch("TauTracks.dEta", &m_trk_dEta);
    m_tree->Branch("TauTracks.dPhi", &m_trk_dPhi);
    m_tree->Branch("TauTracks.z0sinThetaTJVA", &m_trk_z0sinThetaTJVA);
    m_tree->Branch("TauTracks.d0", &m_trk_d0);
    m_tree->Branch("TauTracks.nInnermostPixelHits", &m_trk_nInnermostPixelHits);
    m_tree->Branch("TauTracks.nPixelHits", &m_trk_nPixelHits);
    m_tree->Branch("TauTracks.nSCTHits", &m_trk_nSCTHits);
    m_tree->Branch("TauTracks.isLoose", &m_trk_isLoose);
    m_tree->Branch("TauTracks.passVertexCut", &m_trk_passVertexCut);

    // Cluster variables
    m_tree->Branch("TauClusters.e", &m_cls_e);
    m_tree->Branch("TauClusters.et", &m_cls_et);
    m_tree->Branch("TauClusters.eta", &m_cls_eta);
    m_tree->Branch("TauClusters.phi", &m_cls_phi);
    m_tree->Branch("TauClusters.dEta", &m_cls_dEta);
    m_tree->Branch("TauClusters.dPhi", &m_cls_dPhi);
    m_tree->Branch("TauClusters.SECOND_R", &m_cls_SECOND_R);
    m_tree->Branch("TauClusters.SECOND_LAMBDA", &m_cls_SECOND_LAMBDA);
    m_tree->Branch("TauClusters.CENTER_LAMBDA", &m_cls_CENTER_LAMBDA);

    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::fileExecute ()
{
    // Here you do everything that needs to be done exactly once for every
    // single file, e.g. collect a list of all lumi-blocks processed
    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::changeInput(bool /*firstFile*/)
{
    // Here you do everything you need to do when we change input files,
    // e.g. resetting branch addresses on trees.  If you are using
    // D3PDReader or a similar service this method is not needed.
    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::initialize()
{
    // Here you do everything that you need to do after the first input
    // file has been connected and before the first event is processed,
    // e.g. create additional histograms based on which variables are
    // available in the input files.  You can also create all of your
    // histograms and trees in here, but be aware that this method
    // doesn't get called if no events are processed.  So any objects
    // you create here won't be available in the output if you have no
    // input events.
    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::execute()
{
    // Here you do everything that needs to be done on every single
    // events, e.g. read input variables, apply cuts, and fill
    // histograms and trees.  This is where most of your actual analysis
    // code will go.
    ANA_CHECK_SET_TYPE(EL::StatusCode);

    // EventInfo
    const xAOD::EventInfo *eventInfo = nullptr;
    ANA_CHECK(evtStore()->retrieve(eventInfo, "EventInfo"));
    m_mcEventNumber = eventInfo->mcEventNumber();

    const xAOD::TauJetContainer *taus = nullptr;
    ANA_CHECK(evtStore()->retrieve(taus, "TauJets"));

    for (auto tau : *taus) {
        m_nTracks = tau->auxdata<int>("nTracks");
        m_pt = tau->pt();
        m_eta = tau->eta();
        m_phi = tau->phi();
        m_ptJetSeed = tau->auxdata<float>("trk_ptJetSeed");
        m_etaJetSeed = tau->auxdata<float>("trk_etaJetSeed");
        m_phiJetSeed = tau->auxdata<float>("trk_phiJetSeed");
        m_BDTJetScore = tau->discriminant(xAOD::TauJetParameters::TauID::
                                          BDTJetScore);

        if (m_deco_rnnscore) {
            m_RNNJetScore = tau->auxdata<float>("RNNJetScore");
        }

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
        m_centFrac = tau->auxdata<float>("centFrac");
        m_EMPOverTrkSysP = tau->auxdata<float>("EMPOverTrkSysP");
        m_innerTrkAvgDist = tau->auxdata<float>("innerTrkAvgDist");
        m_ptRatioEflowApprox = tau->auxdata<float>("ptRatioEflowApprox");
        m_dRmax = tau->auxdata<float>("dRmax");
        m_trFlightPathSig = tau->auxdata<float>("trFlightPathSig");
        m_mEflowApprox = tau->auxdata<float>("mEflowApprox");
        m_SumPtTrkFrac = tau->auxdata<float>("SumPtTrkFrac");
        m_absipSigLeadTrk = TMath::Abs(tau->auxdata<float>("ipSigLeadTrk"));
        m_massTrkSys = tau->auxdata<float>("massTrkSys");
        m_etOverPtLeadTrk = tau->auxdata<float>("etOverPtLeadTrk");
        m_ptIntermediateAxis = tau->auxdata<float>("ptIntermediateAxis");

        // Track variables
        m_trk_pt = tau->auxdata<vfloat>("trk_pt");
        m_trk_eta = tau->auxdata<vfloat>("trk_eta");
        m_trk_phi = tau->auxdata<vfloat>("trk_phi");
        m_trk_dEta = tau->auxdata<vfloat>("trk_dEta");
        m_trk_dPhi = tau->auxdata<vfloat>("trk_dPhi");
        m_trk_z0sinThetaTJVA = tau->auxdata<vfloat>("trk_z0sinThetaTJVA");
        m_trk_d0 = tau->auxdata<vfloat>("trk_d0");
        m_trk_nInnermostPixelHits = tau->auxdata<vuint8>(
            "trk_nInnermostPixelHits");
        m_trk_nPixelHits = tau->auxdata<vuint8>("trk_nPixelHits");
        m_trk_nSCTHits = tau->auxdata<vuint8>("trk_nSCTHits");
        m_trk_isLoose = tau->auxdata<vuint8>("trk_isLoose");
        m_trk_passVertexCut = tau->auxdata<vuint8>("trk_passVertexCut");

        // Cluster variables
        m_cls_e = tau->auxdata<vfloat>("cls_e");
        m_cls_et = tau->auxdata<vfloat>("cls_et");
        m_cls_eta = tau->auxdata<vfloat>("cls_eta");
        m_cls_phi = tau->auxdata<vfloat>("cls_phi");
        m_cls_dEta = tau->auxdata<vfloat>("cls_dEta");
        m_cls_dPhi = tau->auxdata<vfloat>("cls_dPhi");
        m_cls_SECOND_R = tau->auxdata<vfloat>("cls_SECOND_R");
        m_cls_SECOND_LAMBDA = tau->auxdata<vfloat>("cls_SECOND_LAMBDA");
        m_cls_CENTER_LAMBDA = tau->auxdata<vfloat>("cls_CENTER_LAMBDA");

        // Fill that puppy
        m_tree->Fill();
    }

    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::postExecute()
{
    // Here you do everything that needs to be done after the main event
    // processing.  This is typically very rare, particularly in user
    // code.  It is mainly used in implementing the NTupleSvc.
    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::finalize()
{
    // This method is the mirror image of initialize(), meaning it gets
    // called after the last event has been processed on the worker node
    // and allows you to finish up any objects you created in
    // initialize() before they are written to disk.  This is actually
    // fairly rare, since this happens separately for each worker node.
    // Most of the time you want to do your post-processing on the
    // submission node after all your histogram outputs have been
    // merged.  This is different from histFinalize() in that it only
    // gets called on worker nodes that processed input events.
    return EL::StatusCode::SUCCESS;
}



EL::StatusCode NtupleCreator::histFinalize()
{
    // This method is the mirror image of histInitialize(), meaning it
    // gets called after the last event has been processed on the worker
    // node and allows you to finish up any objects you created in
    // histInitialize() before they are written to disk.  This is
    // actually fairly rare, since this happens separately for each
    // worker node.  Most of the time you want to do your
    // post-processing on the submission node after all your histogram
    // outputs have been merged.  This is different from finalize() in
    // that it gets called on all worker nodes regardless of whether
    // they processed input events.
    return EL::StatusCode::SUCCESS;
}
