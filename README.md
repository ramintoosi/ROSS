![image](https://github.com/ramintoosi/ROSS/blob/v2/images/Ross_Color.png)

ROSS is an offline spike sorting software implemented based on the methods described in the paper entitled [An automatic spike sorting algorithm based on adaptive spike detection and a mixture of skew-t distributions](https://www.nature.com/articles/s41598-021-93088-w). (Official Implementation)

## Updates:
- **7 January 2022:** Importing .csv files is available on ROSS V2 
- **1 January 2022:** ROSS v2 (beta) is Released! [link](https://github.com/ramintoosi/ROSS/tree/v2)
- **28 September 2021:** We are developing ROSS v2 based on **Python** with new features.
- **06 July 2021:** Our paper is accepted at **Scientific Reports** and is now publicly available (**Open Access**) at [this link](https://www.nature.com/articles/s41598-021-93088-w).

## Introduction
Neural activity monitoring is one of the bases of understanding the brain behavior. The recorded extracellular potential is a combination of multiple neurons activities corrupted by noise. A main step in analyzing the extracellular data is to differentiate among different neuron activities. Spike sorting is the process of assigning each detected spike to the corresponding neurons.
ROSS is a MATLAB based offline spike sorter software which helps the researchers to do automatic and manual spike sorting tasks efficiently. Currently it provides [t-distribution](https://www.sciencedirect.com/science/article/pii/S0165027003001201) and skew-t based methods for automatic spike sorting. Several functions are considered for modifying the auto-sorting results, such as merging and denoising. Also, useful visualizations are provided to get better results.

## Python Version
ROSS v2 is based on Python. Check it out [here](https://github.com/ramintoosi/ROSS/tree/v2).

## Installation

Recommended System

- MATLAB >= 2018b

- 12GB RAM

Download the package to a local folder. Run matlab and navigate to the folder. Then you could easily start Offline Spike Sorter by running “ross.mlapp” or **typing “ross” in the command window**.


## Usage

ROSS provides useful tools for spike detection, automatic sorting and manual sorting. 

- Detection

  You can load raw extracellular data and adjust the provided settings for filtering and thresholding. Then by pushing **Start Detection** button the detection results appear in a PCA plot:

![Spike Detecttion](https://github.com/ramintoosi/ROSS/blob/master/figs/detect_image.png?raw=true)

- Automatic Sorting

  Automatic sorting is implemented based on five different methods: skew-t and t distributions, GMM, k-means and template matching. Several options are provided for configurations in the algorithm. Automatic sorting results will appear in PCA and waveform plots:

![Spike Sorting](https://github.com/ramintoosi/ROSS/blob/master/figs/sorting.png?raw=true)

- Manual Sorting

  Manual sorting tool is used for manual modifications on automatic results by the researcher. These tools include: Merge, Delete, Resort, Denoise, and Manual grouping or deleting samples in PCA domain:

![Manual Sorting](https://github.com/ramintoosi/ROSS/blob/master/figs/manual.png?raw=true)

- Visualization
  
  Several 2D and 3D visualization tools are provided, including inter spike interval, neuron live time, waveforms, 3D plot, and PCA domain plots. Also, you can track detected spikes on the raw data.

![Visualization](https://github.com/ramintoosi/ROSS/blob/master/figs/visualization.PNG?raw=true)

For more instructions and samples please visit [ROSS documentation](https://github.com/ramintoosi/ROSS/blob/master/documentation.pdf), [demo video](https://youtu.be/oxzwZB4WSaI) or [ROSS webpage](https://ramintoosi.github.io/ROSS/).

# Acknowledgment
Thanks to [Plot Big](https://www.mathworks.com/matlabcentral/fileexchange/40790-plot-big).

# Citation
If ROSS helps your research, please cite our paper in your publications.

```
@article{Toosi_2021,
	doi = {10.1038/s41598-021-93088-w},
	url = {https://doi.org/10.1038%2Fs41598-021-93088-w},
	year = 2021,
	month = {jul},
	publisher = {Springer Science and Business Media {LLC}},
	volume = {11},
	number = {1},
	author = {Ramin Toosi and Mohammad Ali Akhaee and Mohammad-Reza A. Dehaqani},
	title = {An automatic spike sorting algorithm based on adaptive spike detection and a mixture of skew-t distributions},
	journal = {Scientific Reports}
}
```
