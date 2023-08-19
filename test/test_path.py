# %% Setup
import sys
sys.path.append('..')

import logging
import os

import matplotlib.pyplot as plt
import numpy as np
from src.path import PathProcessor
from src.config import Origin
from src.plot import display
from src.write import words_from_path

logging.basicConfig(level=logging.INFO)

# %% Test specific word file
logging.basicConfig(level=logging.INFO)
path = np.load("../data/.saves/get.npy")

words_from_path(path, plot=True)

# %%
