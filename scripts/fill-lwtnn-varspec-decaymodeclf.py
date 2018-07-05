#!/usr/bin/env python
import argparse
import json
import h5py
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("preproc", help="preprocessing file")
    parser.add_argument("-i", "--infile", type=argparse.FileType("r"),
                        default="-")
    parser.add_argument("-o", "--outfile", type=argparse.FileType("w"),
                        default="-")

    return parser.parse_args()


def get_preproc(group, scalar=True):
    names = []
    offsets = []
    scales = []

    if scalar:
        idx = ...
    else:
        idx = 0

    for v in group["variables"][...]:
        path = v.decode()
        container, name = path.split("/")
        names.append(name)
        # Converted to lwtnn convention
        offsets.append(-group[path + "/offset"][idx])
        scales.append(1.0 / group[path + "/scale"][idx])

    return names, offsets, scales


if __name__ == "__main__":
    args = get_args()

    config = json.load(args.infile)

    with h5py.File(args.preproc, "r") as f:
        chrg_names, chrg_offsets, chrg_scales = get_preproc(f["chrg_preproc"], scalar=False)
        neut_names, neut_offsets, neut_scales = get_preproc(f["neut_preproc"], scalar=False)
        shot_names, shot_offsets, shot_scales = get_preproc(f["shot_preproc"], scalar=False)
        conv_names, conv_offsets, conv_scales = get_preproc(f["conv_preproc"], scalar=False)

    # Set output layer name
    outputs = config["outputs"]
    assert len(outputs) == 1
    output_layer = config["outputs"][0]

    # Layer name
    output_layer["name"] = "output"

    # Output node names
    assert len(output_layer["labels"]) == 5
    for i, label in enumerate(["1p0n", "1p1n", "1pXn", "3p0n", "3pXn"]):
        output_layer["labels"][i] = label

    # Set input layer variables
    assert len(config["inputs"]) == 0

    input_sequences = config["input_sequences"]
    assert len(input_sequences) == 4

    # Set charged PFO input variables
    layer_names = ["ChargedPFO", "NeutralPFO", "ShotPFO", "ConvTrack"]
    var_names = [chrg_names, neut_names, shot_names, conv_names]
    var_offsets = [chrg_offsets, neut_offsets, shot_offsets, conv_offsets]
    var_scales = [chrg_scales, neut_scales, shot_scales, conv_scales]

    for i, (layer, names, offsets, scales) in enumerate(zip(layer_names, var_names, var_offsets, var_scales)):
        seq = input_sequences[i]
        seq_vars = seq["variables"]

        assert len(seq_vars) == len(names)

        seq["name"] = layer
        for v, n, o, s in zip(seq_vars, names, offsets, scales):
            v["name"] = n
            v["offset"] = float(o)
            v["scale"] = float(s)

    json.dump(config, args.outfile, indent=2)
