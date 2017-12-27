#!/usr/bin/env python
import argparse
import os
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("pattern")
    parser.add_argument("-d", metavar="DIR", default="NtupleCreator")
    parser.add_argument("-n", metavar="NUM", type=int)
    parser.add_argument("--truth", action="store_true")
    parser.add_argument("--rnnscore", action="store_true")

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

    output = ROOT.EL.OutputStream("ntuple")
    job.outputAdd(output)
    ntuple = ROOT.EL.NTupleSvc("ntuple")
    job.algsAdd(ntuple)

    alg = ROOT.NtupleCreator()
    alg.SetName("NtupleCreator")
    alg.m_outputName = "ntuple"
    alg.m_deco_truth = args.truth
    alg.m_deco_rnnscore = args.rnnscore

    job.algsAdd(alg)

    driver = ROOT.EL.DirectDriver()
    driver.submit(job, args.d)
