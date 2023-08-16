import os
import time

import numpy as np

import config as cfg
from controller import XboxController
from keyboard import Origin
from path import PathProcessor, plot_all
from word import WordConstructor

from nltk import ConditionalFreqDist
from nltk.util import bigrams
from collections import Counter
from bigram import select_word, word_set

def words_from_path(path, plot=False):
    # # Remove points where both sticks are near the origin
    # dist1 = np.sqrt(path[:, 0]**2 + path[:, 1]**2)
    # dist2 = np.sqrt(path[:, 2]**2 + path[:, 3]**2)
    # mask = (dist1 > cfg.near_origin) | (dist2 > cfg.near_origin)
    # path = path[mask]

    left_processor = PathProcessor(Origin.LEFT.value, path[:, :2])
    right_processor = PathProcessor(Origin.RIGHT.value, path[:, 2:])
    left_processor.process()
    right_processor.process()
    left_processor.find_min()
    right_processor.find_min()
    # left_processor.filter_peaks()
    # right_processor.filter_peaks()

    if plot:
        plot_all(left_processor, right_processor)

    word_constructor = WordConstructor(left_processor, right_processor)
    word_scores = word_constructor.construct_words()
    return word_scores

if __name__ == '__main__':
    controller = XboxController()
    polling_rate = 100
    prev_word = ''

    print('Ready to write')
    while not controller.X:
        path = np.array([[0, 0, 0, 0]], dtype=float)

        # Wait for Right Bumper to be pressed
        while not controller.RightBumper:
            [lx, ly] = controller.get_left_stick()
            [rx, ry] = controller.get_right_stick()
            path = np.append(path, [[lx, ly, rx, ry]], axis=0)

            time.sleep(1/polling_rate)
        # Wait for Right Bumper to be released
        while controller.RightBumper:
            time.sleep(0.1)

        left_processor = PathProcessor(Origin.LEFT.value, path[:, :2])
        right_processor = PathProcessor(Origin.RIGHT.value, path[:, 2:])
        left_processor.process()
        right_processor.process()
        left_processor.find_min()
        right_processor.find_min()

        word_constructor = WordConstructor(left_processor, right_processor)
        word_scores = word_constructor.construct_words()
        # next_word = select_word(prev_word, word_scores)
        # print(next_word)
        # prev_word = next_word
        print(word_scores[:10])