import os
import pandas as pd
import re


def load_data(file_name, date):
    path = os.path.dirname(os.path.dirname(__file__)) + '/Corpora/'
    corpora = pd.DataFrame()
    for i in file_name:
        for j in date:
            corpora = corpora.append(pd.read_csv(path + '{}{}.csv'.format(i, j)))
    return corpora


class DataPreprocess:
    def __init__(self):
        self.regx_ls = [re.compile(r'([^\s\w])+'),  # keep only alphanumeric characters and spaces.
                        re.compile(r'\b(\w)\b'),  # remove words with only 1 character
                        re.compile(r'\b(\d+)\b'),  # remove number that are fully made of digit
                        re.compile(r'\b(\w+://\S*)\b'),  # remove urls
                        re.compile(r'\b([@|#]\w*)\b')]  # remove hash tag and at

    def regx_parse(self, raw_text):
        for i in range(len(raw_text)):
            for j in self.regx_ls:
                raw_text[i]['Title'] = self._regx_replace(j, raw_text[i]["Title"])
                raw_text[i]['Comments'] = self._regx_replace(j, raw_text[i]["Comments"])
        return raw_text

    def _regx_replace(self, pattern, content):
        content = pattern.sub('', content)
        return content


corpus = load_data(['hot', 'new', 'top'], ['[0628]', '[0709]', '[0422]'])
regx_corpus = DataPreprocess().regx_parse(corpus)
