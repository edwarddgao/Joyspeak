import logging
import math
from operator import itemgetter

from .config import BEAM_WIDTH, Origin
from .keyboard import Keyboard
from .trie import Trie

class WordConstructor:
    trie = Trie()
    ENGLISH_TXT = '../data/english.txt'
    with open(ENGLISH_TXT, "r") as file:
        words = [line.strip() for line in file]
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
                    for char in WordConstructor.trie.next_chars(prefix)
                    # Handle log(0) and avoid duplicates prefixes
                    if prob[char] > 0 and prefix + char not in prefixes
                ]
                new_dup_paths = [
                    {"prefix": prefix + char + char, "score": score + math.log(prob[char])}
                    for char in WordConstructor.trie.next_dup_chars(prefix)
                    # Handle log(0) and avoid duplicates prefixes
                    if prob[char] > 0 and prefix + char + char not in prefixes
                ]
                next_beam.extend(new_paths)
                next_beam.extend(new_dup_paths)
                prefixes.update(map(itemgetter("prefix"), new_paths))
                # Note the case with origin keys, where new prefix added before without penalty
                if prefix and prefix not in prefixes and prob[prefix[-1]] > 0:
                    # Probability that the key is the same as last
                    next_beam.append({"prefix": prefix, "score": score + math.log(prob[prefix[-1]])})
                prefixes.add(prefix)
            # Keep only the top (beam_width) paths
            beam = sorted(next_beam, key=lambda x: x["score"], reverse=True)[:BEAM_WIDTH]
            logging.info(beam[:10])
        # Filter out words
        word_scores = [path for path in beam if WordConstructor.trie.is_word(path["prefix"])]
        return word_scores
