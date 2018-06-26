#!/usr/bin/env python
import argparse
import os
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory",
                        help="Directory containing the samples (as downloaded with rucio)")
    parser.add_argument("pattern",
                        help="Pattern to select samples from `directory`")
    parser.add_argument("-o", "--outfile", metavar="OUTFILE",
                        default="NtupleCreator.root",
                        help="Output ntuple name")
    parser.add_argument("-d", metavar="DIR", default="NtupleCreator",
                        help="Algorithm submit directory")
    parser.add_argument("-n", metavar="NUM", type=int,
                        help="Number of events to run")
    parser.add_argument("--truth", action="store_true",
                        help="Decorate truth information")
    parser.add_argument("--rnnscore", action="store_true",
                        help="Decorate RNNScore (only for --tauid)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tauid", action="store_true",
                       help="Run for tau identification")
    group.add_argument("--decaymodeclf", action="store_true",
                       help="Run for decay mode classification")

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    # Check if submit dir already exists
    if os.path.exists(args.d):
        print("Submit directory already exists - aborting")
        sys.exit(1)

    import ROOT
    ROOT.gROOT.Macro("$ROOTCOREDIR/scripts/load_packages.C")
    ROOT.xAOD.Init().ignore()

    # Search for samples
    sh = ROOT.SH.SampleHandler()

    ROOT.SH.ScanDir() \
           .samplePattern(args.pattern) \
           .samplePostfix("_output.root") \
           .scan(sh, args.directory)

    sh.setMetaString("nc_tree", "CollectionTree")
    sh.setMetaDouble(ROOT.EL.Job.optEventsPerWorker, 1000000)
    sh.printContent()

    # Setup job
    job = ROOT.EL.Job()
    job.sampleHandler(sh)

    if args.n:
        job.options().setDouble(ROOT.EL.Job.optMaxEvents, args.n)

    if args.tauid:
        alg = ROOT.NtupleCreator()
        alg.SetName("NtupleCreator")
        alg.m_deco_rnnscore = args.rnnscore # Only for tauid mode
    elif args.decaymodeclf:
        alg = ROOT.NtupleCreator_DecayModeClf()
        alg.SetName("NtupleCreator")
    else:
        raise RuntimeError("Could not determine run-mode. This should never occur")

    # Common options
    alg.m_outputName = args.outfile
    alg.m_deco_truth = args.truth

    job.algsAdd(alg)

    driver = ROOT.EL.DirectDriver()
    driver.submit(job, args.d)
