import logging
import math
from operator import itemgetter

import config as cfg
from keyboard import Keyboard, Origin
from trie import Trie
from nltk.corpus import brown


class WordConstructor:
    trie = Trie()
    raw_words = brown.words()
    words = [word.lower() for word in raw_words if word.isalpha()]
    for word in set(words):
        trie.insert(word)

    def __init__(self, left, right):
        self.left_path = left.path
        self.right_path = right.path
        self.left_peaks = left.peaks
        self.right_peaks = right.peaks
        
        # Dictionary of every key and associated probability
        self.probs_keys = []

    # Assign a probability to each key based on peak locations
    def _merge_peaks_to_probs(self):
        left_pointer, right_pointer = 0, 0
        # Two pointer traversal of sorted peaks
        while left_pointer < len(self.left_peaks) and right_pointer < len(self.right_peaks):
            if self.left_peaks[left_pointer] < self.right_peaks[right_pointer]:
                point = self.left_path[self.left_peaks[left_pointer]]
                self.probs_keys.append(Keyboard.prob_of_keys(point, Origin.LEFT.value))
                left_pointer += 1
            else:
                point = self.right_path[self.right_peaks[right_pointer]]
                self.probs_keys.append(Keyboard.prob_of_keys(point, Origin.RIGHT.value))
                right_pointer += 1
        while left_pointer < len(self.left_peaks):
            point = self.left_path[self.left_peaks[left_pointer]]
            self.probs_keys.append(Keyboard.prob_of_keys(point, Origin.LEFT.value))
            left_pointer += 1
        while right_pointer < len(self.right_peaks):
            point = self.right_path[self.right_peaks[right_pointer]]
            self.probs_keys.append(Keyboard.prob_of_keys(point, Origin.RIGHT.value))
            right_pointer += 1

    def construct_words(self):
        self._merge_peaks_to_probs()
        beam = [{"prefix": "", "score": 0, 'last_left': '', 'last_right': ''}]
        # prob = probability to each key at a given peak
        for prob in self.probs_keys:
            next_beam = []
            prefixes = set()
            for path in beam:
                prefix, score = path["prefix"], path["score"]
                # Score is kept as log probability
                new_paths = [
                    {"prefix": prefix + char, "score": score + math.log(prob[char])}
                    for char in WordConstructor.trie.next(prefix)
                    # Handle log(0) and avoid duplicates prefixes
                    if prob[char] > 0 and prefix + char not in prefixes
                ]
                next_beam.extend(new_paths)
                prefixes.update(map(itemgetter("prefix"), new_paths))
                # Note the case with origin keys, where new prefix added before without penalty
                if prefix not in prefixes:
                    # Penalize! Can't sit on short prefix with great score
                    next_beam.append({"prefix": prefix, "score": score + math.log(cfg.penalize_score)})
                prefixes.add(prefix)
            # Keep only the top (beam_width) paths
            beam = sorted(next_beam, key=lambda x: x["score"], reverse=True)[:cfg.beam_width]
            logging.info(beam[:10])
        # Filter out words
        word_scores = [path for path in beam if WordConstructor.trie.is_word(path["prefix"])]
        return word_scores
