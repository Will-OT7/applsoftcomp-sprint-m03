# Project template

A simple template for sprint projects. Also check out [data science and
reproducible science cookie
cutters](https://github.com/audreyr/cookiecutter#data-science).

## Installation

Run the following

    ./install.sh YOUR_PROJECT_REPO_FOLDER

This script creates the following folders and files. 

1. `libs` for a software library for the project.
1. `data` for datasets and scripts for downloading datasets.
1. `notebooks` for timestamped experiments.
1. `paper` for manuscripts.
1. `workflow` for workflow scripts.
1. `.gitignore` that lists temporary and binary files to ignore (LaTeX, Python, Jupyter, data files, etc. )
1. `pyproject.toml` for managing Python dependencies using [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Set up

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). And then create a virtual environment using:

Open `pyproject.toml` in a text editor and change the project name and add your project dependencies or create it from scratch using:

```bash 
uv init
```

Then, activate the environment by

```bash
source .venv/bin/activate
```

Then, install the dependencies by running:


```bash 
uv add <package-name>
```

If you need to install non-Python dependencies, you can use conda or mamba as described below.

#### Miniforge

Install miniforge [GitHub - conda-forge/miniforge: A conda-forge distribution.](https://github.com/conda-forge/miniforge).

First create a virtual environment for the project.

    mamba create -n project_env_name python=3.7
    mamba activate project_env_name

Install `ipykernel` for Jupyter. 

    mamba install -y -c bioconda -c conda-forge ipykernel numpy pandas scipy matplotlib seaborn tqdm

Create a kernel for the virtual environment that you can use in Jupyter lab/notebook.

    python -m ipykernel install --user --name project_env_kernel_name
