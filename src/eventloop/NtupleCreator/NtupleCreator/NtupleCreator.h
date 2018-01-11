#ifndef RNN_TAUID_NTUPLECREATOR_H
#define RNN_TAUID_NTUPLECREATOR_H

#include <string>

#include <TTree.h>

#include "EventLoop/Algorithm.h"

class NtupleCreator : public EL::Algorithm
{
    // put your configuration variables here as public variables.
    // that way they can be set directly from CINT and python.
public:
    // float cutValue;

    // variables that don't get filled at submission time should be
    // protected from being send from the submission node to the worker
    // node (done by the //!)
public:
    // For the output tree
    std::string m_outputName;
    bool m_deco_truth;
    bool m_deco_rnnscore;
    TTree *m_tree; //!

    // Variables in the output tree
    unsigned long long m_mcEventNumber; //!
    int m_nTracks; //!
    float m_pt; //!
    float m_eta; //!
    float m_phi; //!
    float m_ptJetSeed; //!
    float m_etaJetSeed; //!
    float m_phiJetSeed; //!
    float m_BDTJetScore; //!

    // RNN Score
    float m_RNNJetScore;

    // Truth variables
    unsigned long m_truthProng; //!
    double m_truthEtaVis; //!
    double m_truthPtVis; //!
    char m_IsTruthMatched; //!
    unsigned long m_truthDecayMode; //!

    // Variables for regular ID
    double m_mu; //!
    int m_nVtxPU; //!
    float m_centFrac; //!
    float m_EMPOverTrkSysP; //!
    float m_innerTrkAvgDist; //!
    float m_ptRatioEflowApprox; //!
    float m_dRmax; //!
    float m_trFlightPathSig; //!
    float m_mEflowApprox; //!
    float m_SumPtTrkFrac; //!
    float m_absipSigLeadTrk; //!
    float m_massTrkSys; //!
    float m_etOverPtLeadTrk; //!
    float m_ptIntermediateAxis; //!

    using vfloat = std::vector<float>;
    using vuint8 = std::vector<uint8_t>;

    // Track variables
    vfloat m_trk_pt; //!
    vfloat m_trk_eta; //!
    vfloat m_trk_phi; //!
    vfloat m_trk_dEta; //!
    vfloat m_trk_dPhi; //!
    vfloat m_trk_z0sinThetaTJVA; //!
    vfloat m_trk_d0; //!
    vuint8 m_trk_nInnermostPixelHits; //!
    vuint8 m_trk_nPixelHits; //!
    vuint8 m_trk_nSCTHits; //!
    vuint8 m_trk_isLoose; //!
    vuint8 m_trk_passVertexCut; //!

    // Cluster variables
    vfloat m_cls_e; //!
    vfloat m_cls_et; //!
    vfloat m_cls_eta; //!
    vfloat m_cls_phi; //!
    vfloat m_cls_dEta; //!
    vfloat m_cls_dPhi; //!
    vfloat m_cls_SECOND_R; //!
    vfloat m_cls_SECOND_LAMBDA; //!
    vfloat m_cls_CENTER_LAMBDA; //!

    // this is a standard constructor
    NtupleCreator ();

    // these are the functions inherited from Algorithm
    virtual EL::StatusCode setupJob (EL::Job& job);
    virtual EL::StatusCode fileExecute ();
    virtual EL::StatusCode histInitialize ();
    virtual EL::StatusCode changeInput (bool firstFile);
    virtual EL::StatusCode initialize ();
    virtual EL::StatusCode execute ();
    virtual EL::StatusCode postExecute ();
    virtual EL::StatusCode finalize ();
    virtual EL::StatusCode histFinalize ();

    // this is needed to distribute the algorithm to the workers
    ClassDef(NtupleCreator, 1);
};

#endif
