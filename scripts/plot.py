#!/usr/bin/env python
import argparse


def main(args):
    import re
    import os
    from os import path
    from glob import glob
    from tqdm import tqdm
    from rnn_tauid.plotting.base import Samples
    from rnn_tauid.plotting.common import ScorePlot

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

    # Create the samples
    inputs = []

    if args.prong_1:
        samples_1p = Samples(
            sig_train=sample_dict.get("sig_1p_train", None),
            sig_test=sample_dict.get("sig_1p_test", None),
            bkg_train=sample_dict.get("bkg_1p_train", None),
            bkg_test=sample_dict.get("bkg_1p_test", None))

        scores_1p = Samples(
            sig_train=score_dict.get("sig_1p_train", None),
            sig_test=score_dict.get("sig_1p_test", None),
            bkg_train=score_dict.get("bkg_1p_train", None),
            bkg_test=score_dict.get("bkg_1p_test", None))

        inputs.append(("1P", samples_1p, scores_1p))

    if args.prong_3:
        samples_3p = Samples(
            sig_train=sample_dict.get("sig_3p_train", None),
            sig_test=sample_dict.get("sig_3p_test", None),
            bkg_train=sample_dict.get("bkg_3p_train", None),
            bkg_test=sample_dict.get("bkg_3p_test", None))

        scores_3p = Samples(
            sig_train=score_dict.get("sig_3p_train", None),
            sig_test=score_dict.get("sig_3p_test", None),
            bkg_train=score_dict.get("bkg_3p_train", None),
            bkg_test=score_dict.get("bkg_3p_test", None))

        inputs.append(("3P", samples_3p, scores_3p))


    plots = [
        ("scoreplot", ScorePlot(bins=50, range=(0, 1))),
        ("scoreplot_log", ScorePlot(plot_train=True, log_y=True, bins=50,
                                    range=(0, 1)))
    ]

    if not path.exists(args.outdir):
        os.mkdir(args.outdir)

    for prong, samples, scores in tqdm(inputs):
        for name, p in tqdm(plots):
            # TODO: Wrap in try block
            fig = p.plot(samples, scores)

            outf_pdf = "{}_{}.pdf".format(name, prong)
            outf_raw = "{}_{}.pkl".format(name, prong)

            fig.savefig(path.join(args.outdir, outf_pdf))
            p.save_raw(path.join(args.outdir, outf_raw))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample-dir", required=True)
    parser.add_argument("-d", "--score-dir", required=True)
    parser.add_argument("-o", "--outdir", default="plots")

    parser.add_argument("-1p", "--1-prong", dest="prong_1", action="store_true")
    parser.add_argument("-3p", "--3-prong", dest="prong_3", action="store_true")

    args = parser.parse_args()
    main(args)
