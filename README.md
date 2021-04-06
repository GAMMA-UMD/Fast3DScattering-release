# Fast3DScattering Repo
This repo contains main codes for our IEEE VR paper ["Learning Acoustic Scattering Fields for Dynamic Interactive Sound Propagation"](https://arxiv.org/abs/2010.04865). 

## Contents
If you have read our paper, you should be aware that this work invovles several separable components, and to fully re-run the work will take weeks for ourselves too because there are several failure points that can occur (mainly simulation/external dependencies). So we try providing the parts that may be useful for other people. But you cannot expect to be able to click-and-run everything in this repo.

## Preparation
To create the conda environment for the deep learning part, please run `conda env create -f environment.yml -n scatter`. But what you really need is a working tensorflow. We do not list Matlab dependencies here.

## Code organization
The folders are organized as follows:
- **mesh_processing** contains codes for mesh preprocessing before feeding to a wave simulator like [FastBEM](https://www.fastbem.com/). For efficiency we implement them using C++ and run the executables. Some batch scripts are provided there for iterating .obj files in a folder. [VCGLIB](https://github.com/cnr-isti-vclab/vcglib) is needed. 
- **simulation** contains codes for initiating FastBEM simulation and data post-processing. The main script is `simSchedule.m` and they are specifically designed to work with a Windows FastBEM (Student Edition) executable.
- **dnn** contains codes for deep learning. The most useful thing for you may be `train.py` and `module.py`, although you should easily be able to use other frameworks. All you need to do is convert the simulation output from FastBEM into a format that your framework recognizes (e.g., `.npy`, `.h5`).
- **utils** contains helper functions to extract/convert simulation data from FastBEM using Python.

## Workflow
1. Pre-process all mesh files using `mesh_processing/trimesh_clustering.cpp`. Remember to double-check which mesh files have abnormal file size and deal with them.
2. Run FastBEM using Matlab scripts in `simulation` folder. More CPUs will drastically reduce simulation time.
3. Extract scattering field data from FastBEM using functions in `utils` folder. Adjust for your intended deep learning framework. 
4. Train your network. Refer to `dnn` folder for our architecture and training procedure.

## Questions
We understand if you have questions since we do not have a lot of energy to refactor our research codes. If you open issues, we will try to discuss with you regarding your goals. But it is not guaranteed that components in this repo can be run in a very smooth way. 

## Citation
If you use our work, please consider citing:
```
@inproceedings{tang2021learning,
  title={Learning Acoustic Scattering Fields for Dynamic Interactive Sound Propagation}, 
  author={Zhenyu Tang and Hsien-Yu Meng and Dinesh Manocha},
  booktitle={IEEE Conference on Virtual Reality and 3D User Interfaces (VR)},
  year={2021},
  organization={IEEE}
}
```