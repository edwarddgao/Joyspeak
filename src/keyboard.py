import numpy as np
import pandas as pd
from .config import RADIUS_LIMIT
from scipy.stats import norm


class Keyboard:
    """Static class representing coordinate system of keyboard layout"""

    layout = [
        {
            "keys": ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            "y": 3,
            "start_x": 0,
        },
        {
            "keys": ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            "y": 1.5,
            "start_x": 0.5,
        },
        {"keys": ["z", "x", "c", "v", "b", "n", "m"], "y": 0, "start_x": 1},
    ]
    # Generate DataFrame with the keys and their coordinates
    data = []
    for row in layout:
        for i, key in enumerate(row["keys"]):
            x = row["start_x"] + i
            y = row["y"]
            data.append([key, x, y])
    pos = pd.DataFrame(data, columns=["Key", "x", "y"])

    @staticmethod
    def angle_to_keys(vec, origin):
        """Return angular difference between vec at origin and each key"""
        df = Keyboard.pos
        origin_coords = df[df["Key"] == origin][["x", "y"]].values[0]
        df["angle"] = np.arctan2(df["y"] - origin_coords[1], df["x"] - origin_coords[0])
        angular_differences = df["angle"] - np.arctan2(vec[1], vec[0])
        angular_differences = np.arctan2(
            np.sin(angular_differences), np.cos(angular_differences)
        )
        angular_differences.index = df["Key"]
        return angular_differences

    @staticmethod
    def dist_from_origin(origin):
        """Return Euclidean distance between origin and each key"""
        df = Keyboard.pos
        origin_coords = df[df["Key"] == origin][["x", "y"]].values[0]
        distances = np.sqrt(
            (df["x"] - origin_coords[0]) ** 2 + (df["y"] - origin_coords[1]) ** 2
        )
        distances.index = df["Key"]  # Ensure index alignment
        return distances

    @staticmethod
    def prob_of_keys(vec, origin):
        """
        Probability distribution for each key based on angle to keys and distance from origin
        Visualize this using kbd_vis.py
        """
        atok = Keyboard.angle_to_keys(vec, origin)
        dfo = Keyboard.dist_from_origin(origin)
        # Domain from [-pi, pi] to [0, 1] where 0 -> 1 and -pi/pi -> 0
        prob_atok = 1 - np.abs(atok) / np.pi
        mag = min(1, np.linalg.norm(vec))
        # Bell curve around origin
        prob_origin = norm.pdf(mag, loc=0, scale=0.3)
        probs = prob_atok * (1 - prob_origin)
        probs[origin] = prob_origin
        probs[dfo > RADIUS_LIMIT] = 0.0
        probs[""] = probs[origin]
        probs = np.clip(probs, 0, 1)
        return probs
