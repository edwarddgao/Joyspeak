import logging

import numpy as np
import pandas as pd
from adjustText import adjust_text
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from keyboard import Keyboard
import config as cfg


class PathProcessor:
    def __init__(self, origin, data):
        self.origin = origin
        self.path = data
        self.angles = None
        self.prob_angle = None
        self.prob_speed = None
        # self.angle_peaks = None
        # self.speed_peak = None
        self.peaks = None

    def _calculate_angle_diff(self):
        diff = np.diff(self.path, axis=0)
        angles = np.arctan2(diff[:, 1], diff[:, 0])
        angle_diffs = np.diff(np.unwrap(angles))
        angle_diffs = np.append(angle_diffs, 0)
        self.angles = np.abs(angle_diffs)

    def process(self):
        path_smooth = gaussian_filter1d(self.path, sigma=2, axis=0)
        self.path = path_smooth
        # self._calculate_angle_diff()
        # self.prob_angle = np.minimum(self.angles / np.pi * cfg.angle_importance, 1)
        speed = np.linalg.norm(np.diff(self.path, axis=0), axis=1)
        if not np.max(speed):
            self.prob_speed = np.zeros_like(speed)
        else:
            self.prob_speed = speed / np.max(speed)
        # append max speed to the end of the array
        self.prob_speed = np.append(self.prob_speed, 0)

    def find_min(self):
        # self.angle_peaks, _ = find_peaks(self.prob_angle, prominence=cfg.peak_prominence)
        # self.speed_peaks, _ = find_peaks(self.prob_speed, prominence=cfg.peak_prominence)
        # self.peaks = np.sort(np.unique(np.concatenate((self.angle_peaks, self.speed_peaks))))
        self.peaks , _ = find_peaks(self.prob_speed, prominence=cfg.peak_prominence)
        self.peaks = np.sort(np.unique(self.peaks))
        logging.info('Peaks: %s', str(self.peaks))
    
    # Remove consecutive peaks that are too close (in direction) together
    def filter_peaks(self):
    # Compute the angles of the peaks
        peak_points = self.path[self.peaks]
        peak_points_angle = np.arctan2(peak_points[:, 1], peak_points[:, 0])
        
        # Compute the absolute differences between consecutive angles
        peak_points_angle_diff = np.abs(np.diff(np.unwrap(peak_points_angle)))

        # Compute the Euclidean distance difference between consecutive peaks
        peak_points_diff = np.sqrt(np.sum(np.diff(peak_points, axis=0)**2, axis=1))

        # Compute a boolean mask indicating which peaks should be kept. A peak should be kept
        # if the difference in angle to the next peak is above the threshold and if the distance
        # is not too close
        keep_mask = np.concatenate(([True], (peak_points_angle_diff > cfg.peak_angle_too_close) & (peak_points_diff > cfg.peak_dist_too_close)))
        self.peaks = self.peaks[keep_mask]
        logging.info('Peaks: %s', str(self.peaks))


def _create_line_segments(points, cmap="viridis", linewidth=3):
    points = np.ma.masked_invalid(points)
    segments = np.concatenate(
        [points[:-1, np.newaxis, :], points[1:, np.newaxis, :]], axis=1
    )
    return LineCollection(segments, cmap=cmap, linewidth=linewidth)

def _plot_path(ax, path, prob_data, peaks, title):
    lc = _create_line_segments(path[:-1])
    lc.set_array(prob_data)
    line = ax.add_collection(lc)
    ax.set_title(title)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.figure.colorbar(line, ax=ax)

    ax.scatter(path[peaks, 0], path[peaks, 1], c="r", s=50)
    texts = [ax.annotate(txt, (path[txt, 0], path[txt, 1]), fontsize=12) for txt in peaks]
    adjust_text(texts, ax=ax)

def arrays_not_empty(*args):
    for arg in args:
        if arg.size == 0:
            return False
    return True

def plot_prob(left_path, right_path, left_prob_data, right_prob_data, left_peaks, right_peaks, title):
    fig, axs = plt.subplots(1, 2, figsize=(20, 10))

    if arrays_not_empty(left_path, left_prob_data, left_peaks):
        _plot_path(axs[0], left_path, left_prob_data, left_peaks, f"Left Joystick - {title}")
    if arrays_not_empty(right_path, right_prob_data, right_peaks):
        _plot_path(axs[1], right_path, right_prob_data, right_peaks, f"Right Joystick - {title}")
    
    plt.tight_layout()
    plt.show()

def plot_all(left_processor, right_processor):
    # plot_prob(
    #     left_processor.path,
    #     right_processor.path,
    #     left_processor.prob_angle,
    #     right_processor.prob_angle,
    #     left_processor.angle_peaks,
    #     right_processor.angle_peaks,
    #     "Probability based on Angle Change (Sharper is better)",
    # )
    plot_prob(
        left_processor.path,
        right_processor.path,
        left_processor.prob_speed,
        right_processor.prob_speed,
        left_processor.peaks,
        right_processor.peaks,
        "Probability based on Speed (Slower is better)",
    )