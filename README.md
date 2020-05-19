# ROSS

ROSS is an offline spike sorting software implemented based on the methods described in the paper entitled [paper]().

## Introduction
Neural activity monitoring is one of the bases of understanding the brain behavior. The recorded extracellular potential is a combination of multiple neurons activities corrupted by noise. A main step in analyzing the extracellular data is to differentiate among different neuron activities. Spike sorting is the process of assigning each detected spike to the corresponding neurons.
ROSS is a MATLAB based offline spike sorter software wich helps the researchers to do automatic and manual spike sorting tasks efficiently. Currently it provides [t-distribution](https://www.sciencedirect.com/science/article/pii/S0165027003001201) and skew-t based methods for automatic spike sorting. Several functions are considered for modifying the auto-sorting results, such as merging and denoising. Also, useful visualizations are provided to get better results.

## Installation

Recommended System

- MATLAB > 2018a

- 12GB RAM

Download the package to a local folder. Run matlab and navigate to the folder. Then you could easily start Offline Spike Sorter by running “main.mlapp” or typing “main” in the command window.


## Usage

ROSS provides useful tools for spike detection, automatic sorting and manual sorting. For more instructions and samples please visit [ROSS documentation]() or [demo video]().

# Acknowledgment
Thanks to [Plot Big](https://www.mathworks.com/matlabcentral/fileexchange/40790-plot-big).

# To Do
- [ ] Upload the skew-t paper on bioarxiv.
- [ ] Complete the ReadMe.
- [ ] Provide a complete documentation.
- [ ] Video Tutorial.
- [ ] Add useful comments to the code.
- [ ] Migrate to python.
- [ ] Add other popular sorting methods.
