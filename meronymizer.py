#!/bin/env python3
# Author: Rafael Leal

import random
import sys
from collections import defaultdict
from itertools import product
from copy import deepcopy
from string import punctuation

import numpy as np
from nltk.corpus import stopwords, wordnet as wn


class Meronymizer:
    STOPS = set(stopwords.words('english')) | set(punctuation)

    def __init__(self, model, ingredients, word=None, bigram_file='uk.lemma.bigrams', encoding='latin1'):
        self.model = model
        self.ingredients = ingredients
        self.synset = self.establish_synset(word)
        self.meronyms = self.build_model_meronyms(self.synset)
        self.new_ingredients = self.match_meronyms_to_list(self.meronyms, self.ingredients)
        print('corresponding ingredients: ', self.new_ingredients)
        self.bigram_dict = self.parse_bigrams(self.new_ingredients, bigram_file, encoding)

    def establish_synset(self, word):
        '''Picks a synset based on wether the user has offered a word or not'''
        if not word:
            synset = self.pick_random_synset()
            print(f"random word: {synset.name()}")
            return synset
        synset = self.pick_similar_synset(word, len(self.ingredients))
        print(f"the word is {synset.name()}")
        return synset

    def find_suitable_synsets(self, min_number_meronyms=5):
        print('Building synset list\n')
        suitable_synsets = []
        for synset in wn.all_synsets():
            # Filtering out open compound words not in model
            # and synsets with too few meronyms
            if self.switch_name(synset.lemma_names()[0]) not in self.model:
                continue
            num_meronyms = len(synset.part_meronyms())
            if num_meronyms < min_number_meronyms:
                continue
            if not self.build_model_meronyms(synset):
                continue
            suitable_synsets.append(synset)
        return suitable_synsets

    def pick_random_synset(self):
        return random.choice(self.find_suitable_synsets())

    def pick_similar_synset(self, word, len_ingredients=5):
        candidates = {self.switch_name(synset.lemma_names())[0]
                      for synset in self.find_suitable_synsets(len_ingredients)}
        candidates = list(candidates - {None})
        most_similar = self.model.most_similar_to_given(word, candidates)
        return wn.synsets(self.switch_name(most_similar))[0]

    def switch_name(self, word):
        '''Switches plain text names between gensin and WordNet formats'''
        if '_' in word:
            return word.replace('_', '::')
        if '::' in word:
            return word.replace('::', '_')
        return word

    #  def find_max_meronyms_synset(self, word):
    #      max_meronyms = max((syn for syn in wn.synsets(word, pos=wn.NOUN)),
    #                         key=lambda x: len(x.part_meronyms()))
    #      return max_meronyms
    #
    #  def print_max_meronyms(self, word):
    #      for synset in self.find_max_meronyms_synset(word).part_meronyms():
    #          print(synset.lemma_names())
    #
    #  def print_meronyms_two_levels(self, word):
    #      for synset in self.find_max_meronyms_synset(word).part_meronyms():
    #          print(f"\nnew synset: {synset.name()}")
    #          synset_name = synset.lemma_names()[0]
    #          self.print_max_meronyms(synset_name)

    def find_representative(self, synset, wordlist, target='n'):
        for word in wordlist:
            word = self.fix_pos(word, target)
            if word in self.model:
                return word
        lemmas = synset.lemma_names()
        if lemmas[0] not in self.model:
            return
        candidates = []
        for word in wordlist:
            for subword in word.split('_'):
                subword = self.fix_pos(subword, target)
                if subword in self.model and subword not in lemmas:
                    candidates.append(subword)
        if not candidates:
            return
        return self.model.most_similar_to_given(lemmas[0], candidates)

    def get_new_ingredients(self):
        return self.new_ingredients

    def get_synset_name(self):
        return self.synset.lemma_names()[0]

    def input_ingredients(self, ingredient_list):
        self.ingredients = ingredient_list
        self.meronyms = self.build_model_meronyms(self.synset)
        self.new_ingredients = self.match_meronyms_to_list(self.meronyms, self.ingredients)
        return self.new_ingredients

    def build_model_meronyms(self, synset, target='n', augment=2):
        '''Fetches meronyms for a given synset. It should also filter out words
           unknown by the gensim model'''
        approved_meronyms = {self.find_representative(synset, part_meronym.lemma_names())
                             for part_meronym in synset.part_meronyms()}
        approved_meronyms = approved_meronyms - {None}
        if not approved_meronyms:
            return
        if augment:
            # Adds similar words to the meronym pool
            extra_words = set()
            for word, score in self.model.most_similar(approved_meronyms, topn=10):
                if word in synset.lemma_names():
                    continue
                checked_word = self.fix_pos(word, target)
                if checked_word:
                    extra_words.add(checked_word)
                    if len(extra_words) >= max((len(approved_meronyms) // 3), augment):
                        break
            approved_meronyms = approved_meronyms | extra_words
        return list(approved_meronyms)

    def sort_meronyms(self, synset, meronym_list):
        '''Returns elements in descending order of similarity.
           Similarity == 1 - distance'''
        synset_name = synset.lemma_names()[0]
        distances = self.model.distances(synset_name, meronym_list)
        return sorted((word for word, distance in zip(meronym_list, distances)),
                      key=lambda x: x[1])

    def match_meronyms_to_list(self, meronyms, matchables):
        '''Input in strings, not synsets. Outputs a list with
           the most similar unique elements from meronym for each matchable'''
        # This is a hack. Unknown meronyms should not come this far
        meronyms = [m for m in meronyms if m in self.model]
        curated_matchables = [m for m in matchables if m in self.model]
        not_found = [n for n in matchables if n not in curated_matchables]
        matrix = np.zeros((len(curated_matchables), len(meronyms)))
        matched_rows = -np.ones(len(curated_matchables))
        matched_columns = -np.ones(len(meronyms))
        for n, element in enumerate(curated_matchables):
            matrix[n] = self.model.distances(element, meronyms)
        for lowest_value in np.sort(matrix, axis=None):
            row, column = np.argwhere(matrix == lowest_value)[0]
            if matched_rows[row] >= 0 or matched_columns[column] >= 0:
                continue
            matched_rows[row] = column
            matched_columns[column] = row
            if len(matched_rows[matched_rows >= 0]) == len(matched_rows):
                break
        results = [meronyms[int(i)] for i in matched_rows]
        for n in not_found:
            results.insert(matchables.index(n), n)
        return results

    def is_meronym_of(self, word, comparator='container', pos=wn.NOUN):
        '''Not in use'''
        comparator = wn.synsets(comparator, pos=pos)[0]
        for synset in wn.synsets(word, pos=pos):
            for path in synset.hypernym_paths():
                if comparator in path:
                    return True
        return False

    def fix_pos(self, word, target):
        '''Tries to find a closely related word with the right POS, in case
           the existing one is not the right kind'''
        if self.check_pos(word, target):
            return word
        return self.convert_word(word, target)

    def check_pos(self, word, target):
        '''Checks if any synset of a certain word has a certain pos.
           This has the added benefit of filtering out odd words'''
        for synset in wn.synsets(word):
            if synset.pos() == target:
                return True
        return False

    def convert_word(self, word, convert_to='n', first_pass=True):
        '''Converts one word into a derivationally related form. In case there is no direct correspondence,
        the algorithm tries to find an intermediate form that will lead to the desired pos.

        noun = 'n'
        verb = 'v'
        adjective = 'a'
        adjective satellite = 's'
        adverb = 'r'
        '''
        poses = ['v', 'n', 'a', 'r', 's']
        poses.remove(convert_to)
        all_candidates = []
        filtered_candidates = []

        for synset in wn.synsets(word):
            for lemma in synset.lemmas():
                all_candidates += lemma.derivationally_related_forms()

        for lemma in all_candidates:
            lemma = lemma.synset().name().split('.', 2)
            if lemma[1] == convert_to:
                filtered_candidates.append(lemma[0])

        # "first_pass" is just a trick to avoid further recursion. There are probably
        # more elegant ways to achieve the same
        if not filtered_candidates and first_pass:
            for pos in poses:
                temp_results = self.convert_word(word, pos, first_pass=False)
                if not temp_results:
                    continue
                possible_results = self.convert_word(temp_results, convert_to, first_pass=False)
                if not possible_results:
                    continue
                return possible_results

        results = sorted((w for w in set(filtered_candidates)),
                         key=lambda x: filtered_candidates.count(x),
                         reverse=True)

        return results[0] if results else None

    def find_closest_hypernyms(self, word1, word2):
        '''As the name indicates. Not in use'''
        hypernym_set = set()
        word1 = wn.synsets(word1)
        word2 = wn.synsets(word2)
        for w1, w2 in product(word1, word2):
            common = w1.lowest_common_hypernyms(w2)
            if common:
                hypernym_set.add(common[0])
        return list(hypernym_set)

    def read_bigrams(self, filename, encoding):
        '''Reads the bigram file and yields its lines'''
        try:
            with open(filename, encoding=encoding) as f:
                for line in f:
                    yield line
        except FileNotFoundError:
            print('''### Please download and extract the file 
                https://wacky.sslmit.unibo.it/lib/exe/fetch.php?media=frequency_lists:uk.lemma.bigrams.7z''')

    def parse_bigrams(self, wordlist, filename, encoding):
        '''Builds a dictionary of collocations and frequencies (it doesn't matter 
           in which direction the words are placed) for the words given'''
        words = set(wordlist)
        bigram_dict = defaultdict(lambda: defaultdict(int))
        for line in self.read_bigrams(filename, encoding):
            line = set(line.split()[1:])
            if line & words:
                new_ingredient = line.intersection(words).pop()
                try:
                    other_word = line.difference(words).pop()
                except KeyError:
                    continue
                if (other_word in Meronymizer.STOPS
                        or other_word not in self.model):
                    continue
                bigram_dict[new_ingredient][other_word] += 1
        for ingredient, values_ in deepcopy(bigram_dict).items():
            for word, count in values_.items():
                if not self.check_pos(word, 'v'):
                    bigram_dict[ingredient].pop(word)

        return bigram_dict

    def find_corresponding_verb(self, word, verb):
        '''Finds semantically similar verbs to the one given'''
        candidates = list(self.bigram_dict[word].keys())
        return self.model.most_similar_to_given(verb, candidates)
