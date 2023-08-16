import math
import nltk
from nltk import FreqDist, ConditionalFreqDist
from nltk.util import bigrams
from nltk.probability import ConditionalProbDist, MLEProbDist
from nltk.corpus import brown



# Tokenizing the Brown corpus
words = brown.words()
word_set = set(words)

# Building bigrams
word_bigrams = list(bigrams(words))

# Frequency distributions
word_freq = FreqDist(words)
bigram_freq = ConditionalFreqDist(word_bigrams)

# Conditional probability distribution
cpd = ConditionalProbDist(bigram_freq, MLEProbDist)

def select_word(previous_word, candidates):
    best_candidate = candidates[0]['prefix']
    best_score = float('-inf')

    if not previous_word:
        return candidates[0]['prefix']

    for candidate in candidates:
        candidate_word = candidate['prefix']
        if candidate_word not in word_set:
            continue
        candidate_log_prob = float(candidate['score'])

        # Bi-gram probability
        bigram_prob = cpd[previous_word].prob(candidate_word)

        if not bigram_prob: continue

        # Combine the lob probabilities
        combined_log_prob = candidate_log_prob + math.log(bigram_prob)

        if combined_log_prob > best_score:
            best_score = combined_log_prob
            best_candidate = candidate_word

    return best_candidate

if __name__ == '__main__':
    # Example usage
    previous_word = "the"
    candidates = [
        {"prefix": "simple", "score": "-12.3"},
        {"prefix": "bi-gram", "score": "-5.3"},
        {"prefix": "brown", "score": "-2.3"}
    ]

    best_next_word = select_word(previous_word, candidates)
    print(f"The best next word after '{previous_word}' is '{best_next_word}'.")
