"""
Description: This module is the course part for DataCamp spaCy data structures.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25

Vocab:
- stores data shared across multiple documents
- to save memory, spaCy encodes all strings to hash values
- strings are only stored once in the StringStore via nlp.vocab.strings
- StringStore: lookup table in both directions
- hashes can' be reversed - that's why we need to provide the shared vocab (it raises an error if the string is not there
- nlp.vocab.strings and doc.vocab.strings work for both
Lexemes:
Definition: They are entries in the vocabulary, e.g. doc = nlp('I love coffee'), lexeme = nlp.vocab['coffee']
=> word text & lexical attributes: lexeme.text, lexeme.orth, lexeme.is_alpha = coffee, 1212...12, True
BUT: Not context-dependent part-of-speech tags, dependencies or entity labels
StringStore:

"""

from spacy.lang.en import English
from spacy.matcher import Matcher
import spacy  # python -m spacy download en_core_web_sm
from DC_spaCy.spacy_basics import SpacyCourseBase


class SpacyCourse4String(SpacyCourseBase):
    def handle_vocab_strings(self):
        vocab_hash = self.nlp.vocab.strings['cat']
        # it doesn't work without a text with that token => we have to use a text with that word included
        # otherwise: we get the error: KeyError: "[E018] Can't retrieve string for hash '5439657043933447811'."
        doc = self.nlp('I bought a cat but accually I wanted to buy a new doc!')
        vocab_string = self.nlp.vocab.strings[vocab_hash]
        print('nlp.vocab: hash={}, string={}'.format(vocab_hash, vocab_string))

        doc = self.nlp('I bought a car but accually I wanted to buy a new bike!')
        vocab_hash = doc.vocab.strings['car']
        vocab_string = doc.vocab.strings[vocab_hash]
        print('doc.vocab: hash={}, string={}'.format(vocab_hash, vocab_string))
