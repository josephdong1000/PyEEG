# PythonEEG

**Analyzes .BIN files generated by companion Matlab code, and generates figures.**

> *Only Windows machines supported. May work on Linux/Mac but requirement versions may need to be changed.*

## Setup (for developing)

- Install Microsoft Visual C++ 14.0 or greater (to get SpikeInterface to work)
  - https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Minimal install required, Visual Studio Build Tools 2022 should be sufficient
- Have Python installed
  - https://www.python.org/downloads/
- Set up the Python environment
  - Create environment: `python -m venv .venv-win`
  - Activate environment: `.venv-win\Scripts\activate`
    - Check that `where python` returns the .venv-win environment first
  - Install requirements: `pip install -r requirements-win.txt`
- Install VSCode, or other appropriate development software
  - https://code.visualstudio.com/
- Program is in `pythoneeg.ipynb`. Set the notebook kernel to `.venv-win`

## Goals

- [ ] Proper git/github repo setup
- [ ] Summary box plots (and show to other labs)
- [ ] Test run over all Marsh dataset
- [ ] Spike sorting
- [ ] Dimensionality reduction
  - [ ] PCA
  - [ ] UMAP / qUMAP
- [ ] Cross-frequency coherence
- [ ] Canonical coherence
- [ ] Peri-spike EEG
- [ ] GUI


## Notes/Changelog

- [10/8/24] Template extractor and function plotter still needed
- [10/7/24] Can read timestamps from .CSVs, matlab code pulls timestamp information from last modified time of .DDF. Added day/night average analysis.
- [10/5/24] `compute_cohere` and `compute_psd` fixed. Metadata date reading still needed. Function plotter still needed. Template extractor from sorting analyzers needs to be written for for figures script.
- [10/4/24] Can read from folders containing BIN and CSV. `compute_cohere` will break if window is too short, added try/except to handle. Same with `compute_psd`, will need to write function to interpolate according to 2nd to last. Metadata needs to read in start timestamp from DDF, or manual input OK
- [10/2/24] Data paths need to be inputted manually. Analysis functions complete (except multi-channel units), but outputs need to be organized and converted to figures by end user; an example is under **Test Analysis Functions**. GUI in progress. Function documentation not written. Set `CONVERT_TO_PY = False` and `CONVERT_PY_TO_EXE = False`