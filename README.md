# ROSS v2

![image](./images/Ross_Color.png)

![ROSS Test](https://github.com/ramintoosi/ROSS/actions/workflows/ross-test.yml/badge.svg)

ROSS v2 (alpha) is the Python version of offline spike sorting software implemented based on the methods described in
the
paper
entitled [An automatic spike sorting algorithm based on adaptive spike detection and a mixture of skew-t distributions](https://www.nature.com/articles/s41598-021-93088-w). (
Official Python Implementation)

### Important Note on ROSS v2

ROSS v2 is implemented based on the client-server architecture. In the alpha version, the GUI and processing units are
completely separated and their connection is based on Restful APIs. Now, you are able to run the light GUI on a simple
machine while the data and algorithms would be executed on a
separate server in your lab. Please carefully read the docs and check our tutorial videos.

## Requirements

- All the requirement packages are listed at environment.yml file in root path

## How to install

1. Git Clone this repository to your local path ```git clone https://github.com/ramintoosi/ROSS```
2. Checkout to v2 ```git checkout v2```
3. Create a conda enviroment by command : ```conda env create -f environment.yml```
4. Activate conda environment ```conda activate ross```

## How to run

1. Run the backend by typing  ```python ./ross_backend/app.py``` in the terminal.
- **optional**: To use a different port use ```python ./ross_backend/app.py --port 5631```.
2. Run the UI by typing  ```python ./ross_ui/main.py``` in the terminal.

**Note:** If you have a separate server, run ```step 1``` in your server and ```step 2``` in your personal computer.

3. The first time you want to use the software, you must define a user as follows:

- In opened window, click on ```Options``` ---> ```Sign In/Up``` , enter the desired username and password, click
  on ```Sign Up```.

4. The next time you want to use the software, just click on ```Options``` ---> ```Sign In/Up``` and enter your username
   and password, click on ```Sign In``` .

5. Import your "Raw Data" as follows :

- In opened window, click on ```File``` ---> ```Import``` ---> ```Raw Data``` , select the data file from your system,
  then, select the variable containing raw-data ```(Spike)``` and click on ```OK```.

6. Enjoy the Software!

For more instructions and samples please visit ROSS documentation at (link), or demo video at (link).

## Usage

ROSS v2, same as v1, provides useful tools for spike detection, automatic and manual sorting.

- Detection

  You can load raw extracellular data and adjust the provided settings for filtering and thresholding. Then by pushing *
  *Start Detection** button the detection results appear in a PCA plot:

  ![image](./images/detection.png)


- Automatic Sorting

  Automatic sorting is implemented based on five different methods: skew-t and t distributions, GMM, k-means and
  template matching. Several options are provided for configurations in the algorithm. Automatic sorting results will
  appear in PCA and waveform plots:

![image](./images/sort.png)

- Manual Sorting

  Manual sorting tool is used for manual modifications on automatic results by the researcher. These tools include:
  Merge, Delete, Resort and Manual grouping or deleting samples in PCA domain:

  ![image](./images/sort2.png)


- Visualization

    - Several visualization tools are provided such as: 3D plot

  ![image](./images/vis1.png)

    - Also, inter spike interval, neuron live time and Cluster Waveforms

  ![image](./images/vis2.png)

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

