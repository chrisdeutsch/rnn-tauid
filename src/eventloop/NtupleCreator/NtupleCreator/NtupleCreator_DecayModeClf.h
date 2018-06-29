#ifndef RNN_TAUID_NTUPLECREATOR_DECAYMODECLF_H
#define RNN_TAUID_NTUPLECREATOR_DECAYMODECLF_H

#include <string>

#include <TTree.h>

#include "EventLoop/Algorithm.h"

class NtupleCreator_DecayModeClf : public EL::Algorithm
{
public:
    // For the output tree
    std::string m_outputName;
    bool m_deco_truth;
    bool m_deco_rnnscore;
    TTree *m_tree; //!

    // Variables in the output tree
    unsigned long long m_mcEventNumber; //!
    float m_mcEventWeight; //!
    int m_nTracks; //!
    float m_pt; //!
    float m_eta; //!
    float m_phi; //!
    float m_BDTJetScore; //!
    float m_BDTJetScoreSigTrans; //!

    // Truth variables
    unsigned long m_truthProng; //!
    double m_truthEtaVis; //!
    double m_truthPtVis; //!
    char m_IsTruthMatched; //!
    unsigned long m_truthDecayMode; //!

    // Variables for regular ID
    double m_mu; //!
    int m_nVtxPU; //!

    using vfloat = std::vector<float>;
    using vint = std::vector<int>;
    using vuint8 = std::vector<uint8_t>;

    // TauJet variables
    float m_jet_Pt; //!
    float m_jet_Phi; //!
    float m_jet_Eta; //!

    // Charged PFO variables
    vfloat m_pfo_chargedPt; //!
    vfloat m_pfo_chargedPhi; //!
    vfloat m_pfo_chargedEta; //!

    // Neutral PFO variables
    vfloat m_pfo_neutralPt; //!
    vfloat m_pfo_neutralPhi; //!
    vfloat m_pfo_neutralEta; //!
    vfloat m_pfo_neutralPi0BDT; //!
    vfloat m_pfo_neutralPtSub; //!
    vuint8 m_pfo_neutralNHitsInEM1; //!
    vfloat m_pfo_neutral_SECOND_R; //!
    vfloat m_pfo_neutral_SECOND_LAMBDA; //!
    vfloat m_pfo_neutral_CENTER_LAMBDA; //!
    vfloat m_pfo_neutral_ENG_FRAC_MAX; //!
    vfloat m_pfo_neutral_ENG_FRAC_CORE; //!
    vfloat m_pfo_neutral_SECOND_ENG_DENS; //!
    vint m_pfo_neutral_NPosECells_EM1; //!
    vint m_pfo_neutral_NPosECells_EM2; //!
    vfloat m_pfo_neutral_secondEtaWRTClusterPosition_EM1; //!
    vfloat m_pfo_neutral_secondEtaWRTClusterPosition_EM2; //!
    vfloat m_pfo_neutral_energyfrac_EM1; //!
    vfloat m_pfo_neutral_energyfrac_EM2; //!

    // Shot PFO variables
    vfloat m_pfo_shotPt; //!
    vfloat m_pfo_shotPhi; //!
    vfloat m_pfo_shotEta; //!

    // Conversion track variables
    vfloat m_conv_pt; //!
    vfloat m_conv_phi; //!
    vfloat m_conv_eta; //!

    // this is a standard constructor
    NtupleCreator_DecayModeClf ();

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
    ClassDef(NtupleCreator_DecayModeClf, 1);
};

#endif
