# Quick Start

Clone the code from the repository the `--recursive` flag is important to also
checkout the lwtnn submodule needed for converting models to be used in
tauRecTools.

```bash
git clone --recursive ssh://git@gitlab.cern.ch:7999/cdeutsch/rnn-tauid.git
```

The setup script in the root directory of the repository sets important
environment variables for later use.

```bash
source rnn-tauid/setup.sh
```

The package requires different software environments for different stages of the
workflow. The different environments are activated by sourcing the scripts in
`rnn-tauid/scripts/setup/`. To use the environments a first time setup for
thehas to be completed. The following compiles the Eventloop algorithms and
creates the python environment needed for training (do not source these scripts
but rather execute them in a subshell):

```bash
setup_eventloop.sh
setup_python.sh
```

The setup of the python environment takes some time as it downloads a standalone
python distribution (miniconda) and all required packages.

After the first time setup you can activate the desired environment with the
activate scripts:

- `source activate_eventloop_env.sh`
    - Activates the eventloop environment for producing flat ntuples from THOR
    MxAODs.
- `source activate_python_env.sh`
    - Activate the python environment for producing HDF5 files from flat
    ntuples, training the networks and evaluating them outside of
    ROOT/Athena/Eventloop.
- `source activate_lwtnn_env.sh`
    - Activate the python environment for converting the model using lwtnn.

For more detailed instructions follow the workflow walkthroughs on Tau
Identification and Tau Decay Mode Classification.

## Related Packages

- [THOR](https://gitlab.cern.ch/atlas-perf-tau/THOR) (Framework to produce MxAODs for TauCP studies)

- [tauRecTools/TauJetRNNEvaluator.h](https://gitlab.cern.ch/atlas/athena/blob/21.0/Reconstruction/tauRecTools/tauRecTools/TauJetRNNEvaluator.h) (Athena implementation of the RNN-based tau identification)

- [tauRecToolsDev/DecayModeClassifier.h](https://gitlab.cern.ch/cdeutsch/tauRecToolsDev/blob/decaymodeclf-implemenation/tauRecToolsDev/DecayModeClassifier.h) (Eventloop implementation of the RNN-based tau decay mode classification)
