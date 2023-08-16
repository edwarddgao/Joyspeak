# %% Setup

import logging
import os

import matplotlib.pyplot as plt
import numpy as np

from word import WordConstructor
from write import words_from_path

# %% Loop through every path file in the saves directory
logging.propagate = False
directory = ".saves"
scores = []

for filename in os.listdir(directory):
    if filename.endswith(".npy"):
        target = filename[:-4]
        path = np.load(f"{directory}/{filename}")
        word_scores = words_from_path(path)
        # Get position of correct word
        position = next(
            (idx for idx, path in enumerate(word_scores) if path["prefix"] == target),
            -1,
        )
        scores.append({
            "target": target,
            "position": position,
            "total": len(word_scores),
            "relative": 1 if position == -1 else position/len(word_scores)
        })

# %% Plot position of words from saves
scores.sort(key=lambda x: x["relative"])
print(scores)

# Calculate percentiles and plot histogram
plt.hist([s['relative'] for s in scores], bins=50, edgecolor="black")
plt.title("Positions Percentile Histogram")
plt.xlabel("Percentile")
plt.ylabel("Frequency")
plt.show()

# Calculate the median position
median = scores[len(scores)//2]["position"]
print(f"Median position: {median}")

# %% Test specific word file
logging.basicConfig(level=logging.INFO)
path = np.load("saves/other.npy")
print(words_from_path(path, plot=True))

# %%
