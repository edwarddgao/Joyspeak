import logging

import numpy as np
from scipy.ndimage import gaussian_filter1d
from .config import SPEED_THRESH, ACC_THRESH, STILL_SPEED


class PathProcessor:
    def __init__(self, origin, data):
        self.origin = origin
        self.path = data
        self.speeds = np.empty(0)
        self.peaks = np.empty(0)

    def process(self):
        """Smooth the path and calculate the speed"""
        path_smooth = gaussian_filter1d(self.path, sigma=2, axis=0)
        self.path = path_smooth
        speed = np.linalg.norm(np.diff(self.path, axis=0), axis=1)
        # Avoid dividing by zero when max speed is 0
        max_speed = np.max(speed)
        if max_speed < STILL_SPEED:
            self.speeds = np.zeros_like(speed)
        else:
            self.speeds = speed / max_speed

    def find_min(self):
        """Find points in path where speed goes from > 0.1 to < 0.1"""
        self.peaks = [
            i
            for i in range(1, len(self.speeds))
            if self.speeds[i - 1] > SPEED_THRESH and self.speeds[i] < SPEED_THRESH
        ]
