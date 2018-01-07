#!/usr/bin/env python
import argparse


def main(args):
    import re
    import os
    from os import path
    from glob import glob
    from tqdm import tqdm
    from rnn_tauid.plotting.common import ScorePlot, ROC, ROCRatio, \
        FlattenerCutmapPlot, FlattenerEfficiencyPlot
    from rnn_tauid.plotting.utils import Sample, SampleHolder

    # Find sample files
    pattern = re.compile(r".*(?P<s>sig|bkg)"
                         r".*(?P<p>1P|3P)"
                         r".*(?P<t>train|test)"
                         r".*\D(?P<idx>\d+)"
                         r".*\.h5$",
                         re.IGNORECASE)

    sample_files = glob(path.join(args.sample_dir, "*.h5"))

    # Build sample dictionary
    sample_dict = dict()
    for s in sample_files:
        m = pattern.search(s)
        d = m.groupdict()
        sample_id = "{s}_{p}_{t}".format(**d).lower()

        # Replace the index in the filename with %d
        sample_dict[sample_id] = re.sub(r"(.*\D)\d+(.*.h5$)", r"\1%d\2",
                                        m.group())

    print("Found samples:")
    print("{:16}{}".format("ID", "Path"))
    for k, v in sample_dict.items():
        print("{:16}{}".format(k, v))

    # Find score files
    score_pattern = re.compile(r".*(?P<s>sig|bkg)"
                               r".*(?P<p>1P|3P)"
                               r".*(?P<t>train|test)"
                               r".*\.h5$",
                               re.IGNORECASE)

    score_files = glob(path.join(args.score_dir, "*.h5"))

    # Build score dictionary
    score_dict = dict()
    for s in score_files:
        m = score_pattern.search(s)
        d = m.groupdict()
        score_id = "{s}_{p}_{t}".format(**d).lower()
        score_dict[score_id] = s

    print("Found scores:")
    print("{:16}{}".format("ID", "Path"))
    for k, v in score_dict.items():
        print("{:16}{}".format(k, v))

    # Merge samples and scores
    merge_dict = {}
    for key in set(sample_dict.keys()) | set(score_dict.keys()):
        if key in sample_dict:
            merge_dict.setdefault(key, []).append(sample_dict[key])
        if key in score_dict:
            merge_dict.setdefault(key, []).append(score_dict[key])

    # Input samples
    inputs = {}

    if args.prong_1:
        samples_1p = SampleHolder(
            sig_train=Sample(*merge_dict["sig_1p_train"]),
            sig_test=Sample(*merge_dict["sig_1p_test"]),
            bkg_train=Sample(*merge_dict["bkg_1p_train"]),
            bkg_test=Sample(*merge_dict["bkg_1p_test"])
        )

        inputs["1P"] = samples_1p

    if args.prong_3:
        samples_3p = SampleHolder(
            sig_train=Sample(*merge_dict["sig_3p_train"]),
            sig_test=Sample(*merge_dict["sig_3p_test"]),
            bkg_train=Sample(*merge_dict["bkg_3p_train"]),
            bkg_test=Sample(*merge_dict["bkg_3p_test"])
        )

        inputs["3P"] = samples_3p


    plots = [
        # ("scoreplot", ScorePlot()),
        # ("scoreplot_log", ScorePlot(log_y=True)),
        # ("scoreplot_comparison", ScorePlot(train=True)),
        # ("scoreplot_comparison_log", ScorePlot(log_y=True, train=True)),
        # ("roc", ROC(["TauJets/BDTJetScore", "TauJets/RNNJetScore", "score"])),
        # ("roc_ratio", ROCRatio([("score", "TauJets/BDTJetScore"),
        #                         ("score", "TauJets/RNNJetScore")]))
        ("flat75", FlattenerCutmapPlot("score", 0.75)),
        ("flat60", FlattenerCutmapPlot("score", 0.6)),
        ("flat45", FlattenerCutmapPlot("score", 0.45)),
        ("flat60_eff", FlattenerEfficiencyPlot("score", 0.6))
    ]

    if not path.exists(args.outdir):
        os.mkdir(args.outdir)

    for key in tqdm(inputs):
        for name, p in tqdm(plots):
            # TODO: Wrap in try block
            fig = p.plot(inputs[key])

            outf_pdf = "{}_{}.pdf".format(name, key)

            fig.savefig(path.join(args.outdir, outf_pdf))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample-dir", required=True)
    parser.add_argument("-d", "--score-dir", required=True)
    parser.add_argument("-o", "--outdir", default="plots")

    parser.add_argument("-1p", "--1-prong", dest="prong_1", action="store_true")
    parser.add_argument("-3p", "--3-prong", dest="prong_3", action="store_true")

    args = parser.parse_args()
    main(args)
