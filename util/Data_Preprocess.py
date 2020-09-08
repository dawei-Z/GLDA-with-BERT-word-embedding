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
        self.regx_ls = [re.compile(r'^https?:\/\/.*[\r\n]*'),  # remove urls
                        re.compile(r'\b([@|#]\w*)\b'),  # remove hash tag and at
                        re.compile(r'[^A-Za-z\s]'),  # keep only alphabetic characters and spaces.
                        re.compile(r'\b(\w)\b'),  # remove words with only 1 character
                        re.compile(r'\b(\d+)\b')]  # remove number that are fully made of digit
        self.unwords = 0

    def preprocess_pipeline(self, raw_text):
        if len(raw_text['Comment'].split()) <= 1:
            print(raw_text['Comment'])
            return None
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
        if 'io' in words:
            words.replace('io', 'iot')
        if 'iiot' in words:
            words.replace('iiot', 'iot')
        return words

    def _stopwords_removal(self, content):
        stop_words = stopwords.words('english')
        stop_words.extend(['nan', 'https', 'http', 'www', 'com'])
        return ' '.join([word for word in simple_preprocess(str(content)) if word not in stop_words])

    def drop_meanless(self, corpus):
        for i in corpus['Title'].values:
            if len(corpus[corpus['Title'] == i]) <= 1:
                index = corpus[corpus['Title'] == i].index
                corpus.drop(index=index, inplace=True)
        for i in corpus['Comment'].values:
            if len(i.split()) <= 1:
                indexes = corpus[corpus['Comment'] == i].index
                corpus.drop(index=indexes, inplace=True)
        return corpus

    def combine_comments(self, corpus):
        new_corpus = pd.DataFrame(columns=['Title', 'Comment'])
        for i in list(set(corpus['Title'].values)):
            if len(corpus[corpus['Title'] == i]) <= 1:
                continue
            if i not in new_corpus['Title'].values:
                comment = '.'.join(corpus[corpus['Title'] == i]['Comment'].values)
                temp = pd.DataFrame({'Title': i, 'Comment': comment}, index=[0])
                new_corpus = new_corpus.append(temp, ignore_index=True)
        return new_corpus


corpus = pd.read_csv(path + 'new_corpus.csv')
corpus = corpus.drop_duplicates()
dp = DataPreprocess()
corpus = dp.drop_meanless(corpus)
print(len(corpus.drop_duplicates(["Title"])))
print(len(corpus))
corpus = corpus.apply(dp.preprocess_pipeline, axis=1)
corpus = corpus.dropna()
print(dp.unwords)
corpus = dp.combine_comments(corpus)
print(len(corpus))
corpus.to_csv(path+'agg_corpora.csv')
