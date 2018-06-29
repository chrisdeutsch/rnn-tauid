# ABI Incompatability (libstdc++) in TensorFlow

If you are working on lxplus or any Tier-3 machine, TensorFlow is likely picking
up the `libstdc++` that comes with the root installation on cvmfs. To solve this
you can prepend the `LD_LIBRARY_PATH` environment variable with the path to the
miniconda libraries:

```bash
export LD_LIBRARY_PATH=${RNN_TAUID_ROOT}/env/miniconda2/lib:${LD_LIBRARY_PATH}
``` 

Doing this will break `root_numpy` as this requires the root libraries instead.
As training (with TensorFlow) and converting ntuples to HDF5 (with `root_numpy`)
are separate steps in the workflow, this should generally not be an issue.
