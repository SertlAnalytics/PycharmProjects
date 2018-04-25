# ColumbiaX: course-v1:ColumbiaX+CSMM.101x+1T2018 - Assigment week 11
# Week 11 Project: NLP - 2018-04-19
# NLP
# Copyright Josef Sertl (https://www.sertl-analytics.com)
# $ python3 driver_3.py
# The training data is provided in the directory "../resource/lib/publicdata/aclImdb/train/" of Vocareum
# CAUTION: Please remove all plotting - will raise an error within the workbench on vocareum

import pandas as pd
import numpy as np
import sys
import os
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import itertools
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix


class Incrementer:
    def __init__(self, subject: str, modulo: int, print: bool):
        self.subject = subject
        self.modulo = modulo
        self.print = print
        self.counter = 0
        self.__print_start__()

    def __print_start__(self):
        if self.print:
            print('...incrementer process {} started...'. format(self.subject))

    def increment(self):
        self.counter += 1
        if self.print and self.modulo > 1:
            if self.counter % self.modulo == 0:
                print(self.counter)


class NLPContentCleaner:
    def __init__(self, local: bool):
        self.local = local
        self.stop_words_path = self.__get_stop_words_path__()
        self.stop_words = []
        self.__init_stop_words__()

    def __get_stop_words_path__(self):
        return 'stopwords.en.txt' if self.local else 'stopwords.en.txt'

    def __init_stop_words__(self):
        df = pd.read_csv(self.stop_words_path, header=None)
        df.columns = ['text']
        for ind, rows in df.iterrows():
            self.stop_words.append(rows.text)

    def get_cleaned_text(self, text: str):
        text = text.strip().lower()
        text = re.sub('[^ a-zA-Z0-9]', ' ', text)  # remove special characters unless space
        text = re.sub(' +', ' ', text)  # remove duplicate white spaces
        return self.__get_word_list_without_stop_words__(text)

    def __get_word_list_without_stop_words__(self, text_input: str):
        return ' '.join([word for word in text_input.split() if word not in self.stop_words])


class TextFileCollector:
    def __init__(self, local: bool):
        self.local = local
        self.content_cleaner = NLPContentCleaner(self.local)
        self.incrementer = Incrementer('TextFileCollector', 1000, True)
        self.root_train_path = self.__get_root_train_path__()
        self.neg_train_text_dict = {}
        self.pos_train_text_dict = {}
        self.imdb_tr_csv_file_name = 'imdb_tr.csv'

    def __get_root_train_path__(self):
        # use terminal to ls files under this directory
        return 'C:/Users/josef/Desktop/temp/aclImdb/train/' if self.local else '../resource/lib/publicdata/aclImdb/train/'

    def read_train_text_files(self):
        for subdir, dirs, files in os.walk(self.root_train_path):
            if subdir.find('neg') > -1 or subdir.find('pos') > -1:
                for file in files:
                    self.incrementer.increment()
                    file_path = subdir + '/' + file
                    if file_path.endswith(".txt"):
                        with open(file_path, encoding="ISO-8859-1") as f:
                            self.__process_file_content__(f.readlines(), subdir.lower(), file.lower())

    def __process_file_content__(self, content, subdir: str, file_name):
        content_list = [x.strip() for x in content]
        content = ' '.join(content_list).lower()
        content_without_stop_word = self.content_cleaner.get_cleaned_text(content)
        # content = re.sub('\W+','', content)
        if subdir.find('neg') > -1:
            self.neg_train_text_dict[file_name] = content_without_stop_word
        elif subdir.find('pos') > -1:
            self.pos_train_text_dict[file_name] = content_without_stop_word

    def write_file_content_to_csv(self):
        row_number = 0
        with open(self.imdb_tr_csv_file_name, 'w') as file_obj:
            file_obj.write('row_number,text,polarity')
            for key in self.pos_train_text_dict:
                row_number += 1
                file_obj.write('\n{},{},{}'.format(row_number, self.pos_train_text_dict[key], 1))
            for key in self.neg_train_text_dict:
                row_number += 1
                file_obj.write('\n{},{},{}'.format(row_number, self.neg_train_text_dict[key], 0))


class UnigramModel:
    def __init__(self, local: bool):
        self.local = local
        self.imdb_tr_csv_file_path = self.__get_imdb_tr_csv_file_path__()
        self.df_csv = None
        self.df_unigram = None
        self.df_unigram_columns = []
        self.sorted_vocabulary = []
        self.sorted_vocabulary_dict = {}
        self.np_array = None
        self.max_rows = 10000

    def __get_imdb_tr_csv_file_path__(self):
        return 'C:/Users/josef/OneDrive/edX/Artificial_Intelligence/Week_11/aclImdb/train/imdb_tr.csv' \
            if self.local else 'imdb_tr.csv'

    def process_tr_csv_file(self):
        self.df_csv = pd.read_csv(self.imdb_tr_csv_file_path, header=0)
        self.init_sorted_vocabulary()
        self.define_df_unigram_columns()
        self.count_words_per_file_for_vocabulary()

    def init_sorted_vocabulary(self):
        row_number = 0
        for ind, row in self.df_csv.iterrows():
            row_number += 1
            self.print_row_number(row_number)
            self.sorted_vocabulary = list(set(self.sorted_vocabulary).union(row.text.split()))
            if row_number > self.max_rows:
                break
        self.sorted_vocabulary.sort()
        for ind, word in enumerate(self.sorted_vocabulary):
            self.sorted_vocabulary_dict[word] = ind

    def define_df_unigram_columns(self):
        self.df_unigram_columns = list(self.sorted_vocabulary)
        self.df_unigram_columns.append('polarity')

    def count_words_per_file_for_vocabulary(self):
        self.np_array = np.zeros([self.df_csv.shape[0], len(self.sorted_vocabulary) + 1], dtype=int)
        row_number = 0
        for ind, row in self.df_csv.iterrows():
            row_number += 1
            self.print_row_number(row_number)
            self.np_array[row_number - 1, self.np_array.shape[1] - 1] = row.polarity
            for words in row.text.split():
                self.np_array[row_number - 1, self.sorted_vocabulary_dict[words]] += 1
            if row_number > self.max_rows:
                break
        self.df_unigram = pd.DataFrame(self.np_array)
        self.df_unigram.columns = self.df_unigram_columns
        print(self.df_unigram.head())

    def print_row_number(self, row_number: int):
        if row_number % 1000 == 0:
            print(row_number)


class NLPClassifierHandler:
    def __init__(self, local: bool):
        self.local = local
        self.ngram_range = (1, 1)
        self.tfidf = False
        self.content_cleaner = NLPContentCleaner(self.local)
        self.imdb_tr_csv_file_path = self.__get_imdb_tr_csv_file_path__()
        self.imdb_te_csv_file_path = self.__get_imdb_te_csv_file_path__()
        self.df_tr = None
        self.tr_row_list = []
        self.df_te = None
        self.te_row_list = []
        self.vectorizer = None
        self.X_train = None
        self.y_train = None
        self.X_test = None

    def __get_vectorizer__(self):
        if self.tfidf:
            return TfidfVectorizer(analyzer='word',
                                   stop_words=self.content_cleaner.stop_words, ngram_range=self.ngram_range)
        else:
            return CountVectorizer(analyzer='word',
                                   stop_words=self.content_cleaner.stop_words, ngram_range=self.ngram_range)

    def __get_imdb_tr_csv_file_path__(self):  # training data for grade evaluation
        return 'imdb_tr.csv' if self.local else 'imdb_tr.csv'

    def __get_imdb_te_csv_file_path__(self):  # test data for grade evaluation
        return 'C:/Users/josef/OneDrive/edX/Artificial_Intelligence/Week_11/aclImdb/test/imdb_te.csv' \
            if self.local else '../resource/asnlib/public/imdb_te.csv'

    def load_data(self):
        self.__load_tr_data__()
        self.__load_te_data__()

    def __load_tr_data__(self):
        print('Load training data...')
        self.df_tr = pd.read_csv(self.imdb_tr_csv_file_path, header=0, encoding="ISO-8859-1")
        self.tr_row_list = self.get_row_list(self.df_tr)

    def __load_te_data__(self):
        print('Load test data...')
        self.df_te = pd.read_csv(self.imdb_te_csv_file_path, header=0, encoding="ISO-8859-1")
        self.te_row_list = self.get_row_list(self.df_te)

    def run_vectorizer_on_model(self, ngram: int, tfidf: bool):
        print('Run_Vectorizer_On_Model with ngram = {} and tfidf = {}'.format(ngram, tfidf))
        self.ngram_range = ngram
        self.tfidf = tfidf
        self.vectorizer = self.__get_vectorizer__()
        self.__run_vectorizer_for_tr_data__()
        self.__run_vectorizer_for_te_data__()
        # self.__transform_by_tfidf__()
        self.__run_sgd_classifier__()

    def __run_vectorizer_for_tr_data__(self):
        self.vectorizer.fit(self.tr_row_list)
        # self.__print_vectorizer_vocabulary__(10)
        self.X_train = self.vectorizer.transform(self.tr_row_list)
        print('self.X_train.shape={}'.format(self.X_train.shape))
        self.y_train = np.array(self.df_tr.polarity)

    def __run_vectorizer_for_te_data__(self):
        self.X_test = self.vectorizer.transform(self.te_row_list)

    def __transform_by_tfidf__(self):
        if self.tfidf:
            tdidf_transformer = TfidfTransformer(norm='l1', use_idf=True)
            self.X_train = tdidf_transformer.fit_transform(self.X_train)
            self.X_test = tdidf_transformer.fit_transform(self.X_test)

    def get_row_list(self, df: pd.DataFrame):
        incrementer = Incrementer('Get_Row_List', 1000, True)
        row_number = 0
        text_list = []
        for ind, row in df.iterrows():
            incrementer.increment()
            text_cleaned = self.content_cleaner.get_cleaned_text(row.text)
            text_list.append(text_cleaned)
        return text_list

    def __print_vectorizer_vocabulary__(self, elements: int = 2):
        print(dict(itertools.islice(self.vectorizer.vocabulary_.items(), elements)))

    def __run_sgd_classifier__(self):
        reg = SGDClassifier(loss='hinge', penalty='l1')
        if self.__run_cross_validation__(reg):
            reg.fit(self.X_train, self.y_train)
            predictions = reg.predict(self.X_test)
            self.__write_prediction_to_file__(predictions)
        else:
            print('Accuracy is not enough...')

    def __run_cross_validation__(self, reg):
        X_train, X_test, y_train, y_test = train_test_split(self.X_train, self.y_train, test_size=0.40, stratify=self.y_train)
        reg.fit(X_train, y_train)
        predictions = reg.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        cnf_matrix = confusion_matrix(y_test, predictions)
        print(cnf_matrix)
        print('Accuracy for SGDClassifier = {}'.format(accuracy))
        return True if accuracy > 0.40 else False

    def __write_prediction_to_file__(self, prediction: np.array):
        with open(self.__get_output_file_name__(), 'w') as file_obj:
            for i in prediction:
                file_obj.write(str(i) + '\n')
        print('File written: {}'.format(file_obj.name))

    def __get_output_file_name__(self):
        if self.ngram_range[1] == 1:
            if self.tfidf:
                return 'unigramtfidf.output.txt'
            else:
                return 'unigram.output.txt'
        else:
            if self.tfidf:
                return 'bigramtfidf.output.txt'
            else:
                return 'bigram.output.txt'


def imdb_data_preprocess(inpath, outpath="./", name="imdb_tr.csv", mix=False):
    '''Implement this module to extract
   and combine text files under train_path directory into
   imdb_tr.csv. Each text file in train_path should be stored
   as a row in imdb_tr.csv. And imdb_tr.csv should have two
   columns, "text" and label'''
    pass

local = True

if not local:
    text_file_collector = TextFileCollector(local)
    text_file_collector.read_train_text_files()
    text_file_collector.write_file_content_to_csv()

nlp_classifier = NLPClassifierHandler(local)
nlp_classifier.load_data()

for ngram_range in [(1, 1), (1, 2)]:
    for tfidf in [False, True]:
        nlp_classifier.run_vectorizer_on_model(ngram_range, tfidf)
