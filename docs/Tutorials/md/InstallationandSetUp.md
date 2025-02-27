# 🎯 Setting up CSPOT 

### Kindly note that **CSPOT is not a plug-and-play solution**, rather it's a framework that requires significant upfront investment of time from potential users for training and validating deep learning models, which can then be utilized in a plug-and-play manner for processing large volumes of similar multiplexed imaging data.

**There are two ways to set it up based on how you would like to run the program**
- Using an interactive environment like Jupyter Notebooks
- Using Command Line Interface

Before we set up CSPOT, we highly recommend using a environment manager like Conda. Using an environment manager like Conda allows you to create and manage isolated environments with specific package versions and dependencies. 

**Download and Install the right [conda](https://docs.conda.io/en/latest/miniconda.html) based on the opertating system that you are using**

We have tested the following 
- Linux (CPU, GPU)
- Windows (CPU, GPU)
- Windows WSL (CPU, GPU)
- Mac: Intel (CPU)
- Mac M1 or M2 (CPU)

<hr>

## Let's create a new conda environment and install CSPOT

use the terminal (mac/linux) and anaconda promt (windows) to run the following command
```
conda create --name cspot -y python=3.9
```

**Install `CSPOT` within the conda environment.**

```
conda activate cspot
pip install cspot
```

## If you would like CSPOT to use GPU:
cspot uses Tensorflow. Please install necessary packages for tensorflow to recogonise your specific GPU.  
We have tested the following command in windows machine using nvidia GPU. Does not work on windows WSL2 due to tensorflow's dependency issues.

```
conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0 -y 
```

<hr>

## Download the Exemplar Dataset
To help you get used to the program we have provided some dummy data.   
**Download link to the [exemplar dataset provided here.](https://doi.org/10.7910/DVN/C45JWT)**  
All of the following files are mandatory for running cspot, but `phenotype_workflow.csv` is optional and can be skipped if single cell phenotyping is not required. `manuscriptModels` is provided explicitly for going through this tutorial. 
```
cspotExampleData/
├── image
│   └── exampleImage.tif
├── manuscriptModels
│   ├── CD3D
│   ├── CD4
│   ├── CD45
│   ├── CD8A
│   ├── ECAD
│   └── KI67
├── markers.csv
├── phenotype_workflow.csv
├── quantification
│   └── exampleSpatialTable.csv
└── segmentation
    └── exampleSegmentationMask.tif
```

<hr>

## Method 1: Set up Jupyter Notebook (If you would like to run CSPOT in an interactive setting)
Install jupyter notebook within the conda environment
```
conda activate cspot
pip install notebook
```
After installation, open Jupyter Notebook by typing the following command in the terminal, ensuring that the cspot environment is activated and you are within the environment before executing the jupyter notebook command.
```
jupyter notebook
```
We will talk about how to run cspot in the next tutorial.

<hr>

## Method 2: Set up Command Line Interface (If you like to run CSPOT in the CLI, HPC, etc)

Activate the conda environment that you created earlier

```
conda activate cspot
```

**MAC / LINUX / WSL**  
If you have git installed you can clone the repo with the following command
```
git clone https://github.com/nirmallab/cspot
cd cspot/cspot/
```

*OR*  

```
wget https://github.com/nirmalLab/cspot/archive/main.zip
unzip main.zip 
cd cspot-main/cspot 
```

**WINDOWS**  
If you have git installed you can pull the repo with the following command
```
git clone https://github.com/nirmallab/cspot
```

*OR*  
  
Head over to https://github.com/nirmallab/cspot in your browser and download the repo.



<hr>

## Method 3: Set up Docker

Follow the docker installation guide to install docker: https://docs.docker.com/engine/install/

**Download CSPOT from Docker Hub**
```
docker pull nirmallab/cspot:latest
```

There is a special tutorial on how to run cspot with docker, please refer to that for further instructions.


```python

```
