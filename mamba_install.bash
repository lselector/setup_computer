#! /bin/bash

# -------------------------------------
# script to install modules using mamba (python package manager)
# mamba is a reimplementation of the conda package manager in C++.
# It features parallel downloading and faster dependency solving
# To use, first download and install miniconda
#   https://docs.conda.io/en/latest/miniconda.html
# Make sure that these directories added to PATH:
#     $HOME/miniconda3/condabin
#     $HOME/miniconda3/bin
# Then install mamba:
#   https://github.com/mamba-org/mamba
# -------------------------------------

conda update -y -n base -c defaults conda
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install -y mamba -n base -c conda-forge
# -------------------------------------
mamba install -y notebook        # jupyter Notebook
mamba install -y jupyterlab      # jupyter Lab
mamba install -y ipywidgets      # browser widgets
mamba install -y numpy
mamba install -y pandas
mamba install -y scikit-learn
mamba install -y statsmodels
mamba install -y xgboost
mamba install -y hdbscan -c conda-forge # clustering

mamba install -y matplotlib
mamba install -y plotly 
mamba install -y dash
mamba install -y seaborn
mamba install -y plotnine
# -------------------------------------
mamba install -y numba==0.53   # shap depends on specific numba
mamba install -y shap          # ML feature analysis
# -------------------------------------
mamba install -y pytube        # download youtube videos
# -------------------------------------

# -------------------------------------
# rarely needed
# -------------------------------------
# termcolor
# pivottablejs
# pyspark
# -------------------------------------
# ipython-sql
# sql
# mysql-connector-python
# pyyaml
# -------------------------------------
# google-api-python-client
# google-auth-httplib2
# google-auth-oauthlib
# -------------------------------------
# h2o
# imblearn
# speech_recognition
# -------------------------------------
