# RNN-TauID

## Setup

1. Set enviroment variables with `source setup.sh`
2. Compile eventloop variables with `setup_eventloop.sh` (optional)
3. Create python environments with `setup_python.sh` (optional)
4. Activate environments with `source activate_*_env.sh` where `*` is
   `eventloop`, `python` or `lwtnn`

## Workflow

1. Produce MxAODs on the grid with THOR
2. Flatten MxAODs
3. Produce hdf5 files for training
4. Train
5. Evaluate

## Related packages

- [THOR](https://gitlab.cern.ch/cdeutsch/THOR/tree/RNN-MC16A)
- [tauRecToolsDev](https://gitlab.cern.ch/cdeutsch/tauRecToolsDev/tree/RNN-MC16A)

TODO: Explain workflow including external packages

## Convert trained model

```
lwtnn-split-keras-network.py model.h5
kerasfunc2json.py architecture.json weights.json | fill-lwtnn-varspec.py preproc.h5 | kerasfunc2json.py architecture.json weights.json /dev/stdin > nn.json
```

## TODOs

- Implement the most important plots for performance evaluation
    - Create subpackage for plotting incl. a plot class for defining the plots
    - Partial dependence plots?
    - Always save raw data to recreate the plot (pickle?)
- Port training implementation
- Write an evaluator using lwtnn and eventloop (produce slim MxAOD output)
- Write a one-shot script to do everything
- Explain sample naming convention
