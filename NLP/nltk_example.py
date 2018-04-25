import pandas as pd
import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import TreebankWordTokenizer

print(type(state_union))
train_text = state_union.raw('2005-GWBush.txt')
sample_text = state_union.raw('2006-GWBush.txt')
german_text = 'Der erste Satz war gestern nicht richtig gesprochen worden. ' \
              'Daher werde ich ihn heute am 25.04.2018 nochmals wiederholen. ' \
              'Morgen sollte es dann möglich sein, den Inhalt korrekt wieder zu geben.'

custom_sent_tokenizer = PunktSentenceTokenizer(train_text)
tokenized = custom_sent_tokenizer.tokenize(sample_text)

for i in tokenized:
    words = nltk.word_tokenize(i)
    tagged = nltk.pos_tag(words)
    # print('i={}, \ntagged={}'.format(i, tagged))
    break

german_custom_sent_tokenizer = TreebankWordTokenizer()
german_tokenized = custom_sent_tokenizer.tokenize(german_text)

# german_tokenizer = nltk.data.load(resource_url='tokenizers/punkt/german.pickle')
# german_sentences = german_tokenizer.tokenize(german_text)
# print(german_sentences)

for i in german_tokenized:
    words = nltk.word_tokenize(i, language='german')
    tagged = nltk.pos_tag(words)
    print('i={}, \ntagged={}'.format(i, tagged))

corp = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09',
                                     ['ignore', 'words', 'ignore', 'ignore', 'pos'],
                                     encoding='utf-8')

print(corp)

import random

tagged_sents = corp.tagged_sents()
print(tagged_sents)
random.shuffle(tagged_sents)









