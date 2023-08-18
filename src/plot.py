import logging
import numpy as np
from adjustText import adjust_text
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection


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
    logging.info(peaks)
    if peaks:
        ax.scatter(path[peaks, 0], path[peaks, 1], c="r", s=50)
        texts = [
            ax.annotate(txt, (path[txt, 0], path[txt, 1]), fontsize=12) for txt in peaks
        ]
        adjust_text(texts, ax=ax)


def path_speed(
    left_path,
    right_path,
    left_speed,
    right_speed,
    left_peaks,
    right_peaks,
    title,
):
    fig, axs = plt.subplots(1, 2, figsize=(20, 10))
    _plot_path(axs[0], left_path, left_speed, left_peaks, f"Left Joystick - {title}")
    _plot_path(
        axs[1],
        right_path,
        right_speed,
        right_peaks,
        f"Right Joystick - {title}",
    )

    plt.tight_layout()
    plt.show()


def kinematics(left_speed, right_speed):
    fig, axs = plt.subplots(1, 2, figsize=(20, 10))
    axs[0].plot(left_speed)
    left_acc = np.diff(left_speed)
    axs[0].plot(left_acc)
    left_jerk = np.diff(left_acc)
    axs[0].plot(left_jerk)

    axs[1].plot(right_speed)
    right_acc = np.diff(right_speed)
    axs[1].plot(right_acc)
    right_jerk = np.diff(right_acc)
    axs[1].plot(right_jerk)

    return left_jerk, right_jerk


def display(left_processor, right_processor):
    left_peaks, right_peaks = kinematics(left_processor.speeds, right_processor.speeds)
    path_speed(
        left_processor.path,
        right_processor.path,
        left_processor.speeds,
        right_processor.speeds,
        left_processor.peaks,
        right_processor.peaks,
        "Probability based on Speed (Slower is better)",
    )
    
