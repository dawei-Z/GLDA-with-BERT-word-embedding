import os
import pandas as pd
import re
from spellchecker import SpellChecker
import nltk
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
import sys


path = os.path.dirname(os.path.dirname(__file__)) + '/Corpora/'


def load_data(file_name, date):

    corpora = pd.DataFrame()
    for i in file_name:
        for j in date:
            corpora = corpora.append(pd.read_csv(path + '{}{}.csv'.format(i, j)))
    return corpora


class DataPreprocess:
    def __init__(self):
        self.regx_ls = [re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)))'),  # remove urls
                        re.compile(r'[^A-Za-z0-9\s ]'),  # keep only alphanumeric characters and spaces.
                        re.compile(r'\b(\w)\b'),  # remove words with only 1 character
                        re.compile(r'\b(\d+)\b'),  # remove number that are fully made of digit
                        re.compile(r'\b([@|#]\w*)\b')]  # remove hash tag and at
        self.unwords = 0

    def preprocess_pipeline(self, raw_text):
        for i in ['Title', 'Comment']:
            raw_text[i] = self._stopwords_removal(raw_text[i])
            for j in self.regx_ls:
                raw_text[i] = raw_text[i].lower()
                raw_text[i] = self._regx_replace(j, raw_text[i])
            raw_text[i] = self._spell_check(raw_text[i])
            raw_text[i] = self._lemmatise(raw_text[i])
            raw_text[i] = ' '.join(raw_text[i])

        return raw_text

    def _regx_replace(self, pattern, content):
        content = pattern.sub('', content)
        return content

    def _lemmatise(self, content):
        clean = []
        lemmatiser = nltk.stem.WordNetLemmatizer()
        tokens = self._tokenization(content)
        tags = nltk.pos_tag(tokens)
        for word, tag in tags:
            tag = self._tag_conversion(tag)
            if tag:
                clean.append(lemmatiser.lemmatize(word, tag))
            else:
                clean.append(word)
        return clean

    def _tokenization(self, content):
        return nltk.tokenize.word_tokenize(content)

    def _tag_conversion(self, tag):
        """convert POS tag to lemmatiser tag"""
        tag = tag[0]
        wn = nltk.corpus.wordnet
        tag_dict = {'J': wn.ADJ,
                    'V': wn.VERB,
                    'N': wn.NOUN,
                    'R': wn.ADV}
        return tag_dict.get(tag, None)

    def _spell_check(self, words):
        spell = SpellChecker()
        tokens = self._tokenization(words)
        misspelled = spell.unknown(tokens)
        if misspelled:
            for i in misspelled:
                # print("Unknown: {}".format(i))
                # print("Correction: {}".format(spell.correction(i)))
                # value = input("Correct?\n")
                # if value == "y":
                words.replace(i, spell.correction(i))
                self.unwords += 1
        return words

    def _stopwords_removal(self, content):
        stop_words = stopwords.words('english')
        return ' '.join([word for word in simple_preprocess(str(content)) if word not in stop_words])


corpus = pd.read_csv(path+'new_corpus.csv')
corpus = corpus.drop_duplicates()
print(len(corpus.drop_duplicates(["Title"])))
print(len(corpus))
dp = DataPreprocess()
corpus = corpus.apply(dp.preprocess_pipeline, axis=1)
print(dp.unwords)
corpus.to_csv(path+'new_clean_corpora.csv')
