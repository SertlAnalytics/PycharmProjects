"""
Description: This module is the course part for DataCamp spaCy data structures.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25

doc:
- its instantiated when using the nlp object for a text or by using the Doc object:

span:
- its instantiated when using the doc object or by using the Span object

token:
- see example "find_a_verb_after_a_proper_noun" within the SpacyCourseBase class to see how to work with tokens
Summary:
a) Doc and Span are very powerful and hold references and relationships of words and sentences
b) If you wish your output as string: Convert results to strings as late as possible, otherwise you lose all relationships
c) Use token attributes if available - e.g. token.i for token index
d) Don't forget to pass in the shared vocab
"""

from spacy.tokens import Doc, Span
from DC_spaCy.spacy_basics import SpacyCourseBase


class SpacyCourse4DocSpanToken(SpacyCourseBase):
    def handle_doc(self):
        # instantiate by text
        doc = self.nlp('I bought a cat but actually I wanted to buy a new doc!')
        self.__print_tokens_for_doc__(doc)
        # initiate by Doc class
        words = ['Hello', 'world', '!']
        spaces = [True, False, False]
        doc = Doc(self.nlp.vocab, words=words, spaces=spaces)
        self.__print_tokens_for_doc__(doc)

    def handle_span(self, print_tokens=False, print_ents=False):
        for k in range(0, 2):
            if k == 0:  # instantiate by doc
                doc = self.nlp('I bought a cat but actually I wanted to buy a new doc!')
                span_with_label = Span(doc, 1, 7, label='ByDoc')
            else:
                # initiate by Span class
                words = ['Hello', 'world', '!']
                spaces = [True, False, False]
                doc = Doc(self.nlp.vocab, words=words, spaces=spaces)
                span_with_label = Span(doc, 1, 3, label='Manually')
            self.__print_text_for_doc__(doc)
            if print_tokens:
                self.__print_tokens_for_doc__(doc)
            if print_ents:
                self.__print_entities_for_doc__(doc)
            doc.ents = [span_with_label]
            if print_ents:
                self.__print_entities_for_doc__(doc)

    def handle_token(self):
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
