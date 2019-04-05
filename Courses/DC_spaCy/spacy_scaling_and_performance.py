"""
Description: This module is the course part for DataCamp spaCy scaling and performance.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-04-01

Processing large volumes of text:
- use nlp.pipe method
- processes texts as a stream, yields Doc objects
- much faster than calling nlp on each text
BAD: docs = [nlp(text) for text in LOTS_OF_TEXTS]
GOOD: docs = list(nlp.pipe(LOTS_OF_TEXTS))
Passing in context (1):
- setting as_tuples=True on nlp.pipe lets you pass in (text context) tupls -> (doc, context) tuple
- useful for associating metadata with the doc
- Example: see below "passing_context_as_tuple"
Passing in context (2): using exensions...
- Example: see below "passing_context_with_extensions_as_tuple"
Using only the tokenizer (remember: Pipeline[tokenizer - tagger - parser - ner - ...] -> Doc)
- avoid calling other pipelines components to be called - this is much faster when you don't need the other components
- BAD: doc = self.nlp('Hello world'), GOOD: doc = self.nlp.make_doc('Hello world')
Disabling pipeline components
- use nlp.disable_pipes to temporarily disable one or more pipes
- Example: disable_pipeline_components_temporarily
"""

from spacy.tokens import Doc
from DC_spaCy.spacy_basics import SpacyCourseBase
from datetime import datetime


class SpacyCourse4Scaling(SpacyCourseBase):
    def __init__(self, model=''):
        SpacyCourseBase.__init__(self, model)

    def process_large_volume_of_text(self):
        text_01 = 'This is my disable pipeline component test. This is done by my friend Markus.'
        text_02 = 'This is my disable pipeline component test. This is done by my friend Markus.'
        text_list = [text_01, text_02]
        print(datetime.now())
        docs = [self.nlp(text) for text in text_list]  # bad
        print(datetime.now())
        docs = list(self.nlp.pipe(text_list))  # good
        print(datetime.now())
        # Create a list of patterns for the PhraseMatcher
        people = ['David Bowie', 'Angela Merkel', 'Lady Gaga']
        patterns = list(self.nlp.pipe(people))

    def passing_context_as_tuple(self):
        data = [('this is a text', {'id': 1, 'page_number': 15}), ('and another text', {'id': 2, 'page_number': 16})]
        for doc, context in self.nlp.pipe(data, as_tuples=True):
            print(doc.text, context['page_number'])

    def passing_context_with_extensions_as_tuple(self):
        Doc.set_extension('id', default=None)
        Doc.set_extension('page_number', default=None)
        data = [('this is a text', {'id': 1, 'page_number': 15}), ('and another text', {'id': 2, 'page_number': 16})]
        for doc, context in self.nlp.pipe(data, as_tuples=True):
            doc._.id = context['id']
            doc._.page_number = context['page_number']
            print(doc.text, context['page_number'])

    def example_passing_context_with_extension_as_tuple(self):
        DATA = self.__get_data_for_exercise__()
        Doc.set_extension('book', default=None, force=True)
        Doc.set_extension('author', default=None, force=True)
        for doc, context in self.nlp.pipe(DATA, as_tuples=True):
            # Set the doc._.book and doc._.author attributes from the context
            doc._.book = context['book']
            doc._.author = context['author']
            # Print the text and custom attribute data
            print(doc.text, '\n', "— '{}' by {}".format(doc._.book, doc._.author), '\n')

    def using_only_the_tokenizer(self):
        print(datetime.now())
        doc = self.nlp('Hello world')  # BAD
        print(datetime.now())
        doc = self.nlp.make_doc('Hello world')  # GOOD
        print(datetime.now())
        """
        2019-04-01 11:30:31.085851
        2019-04-01 11:30:31.094799
        2019-04-01 11:30:31.094799
        """

    def disable_pipeline_components_temporarily(self):
        with self.nlp.disable_pipes('tagger', 'parser'):
            text = 'This is my disable pipeline component test. This is done by my friend Markus.'
            doc = self.nlp(text)
            print(doc.ents)
        # comment: restores the pipes after the with block

    def __get_data_for_exercise__(self):
        return [('One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed '
                 'into a horrible vermin.', {'book': 'Metamorphosis', 'author': 'Franz Kafka'}),
                ("I know not all that may be coming, but be it what it will, I'll go to it laughing.",
                 {'book': 'Moby-Dick or, The Whale', 'author': 'Herman Melville'}),
                ('It was the best of times, it was the worst of times.',
                 {'book': 'A Tale of Two Cities', 'author': 'Charles Dickens'}),
                ('The only people for me are the mad ones, the ones who are mad to live, mad to talk, '
                 'mad to be saved, desirous of everything at the same time, the ones who never yawn or say a '
                 'commonplace thing, but burn, burn, burn like fabulous yellow roman candles exploding like '
                 'spiders across the stars.', {'book': 'On the Road', 'author': 'Jack Kerouac'}),
                ('It was a bright cold day in April, and the clocks were striking thirteen.',
                 {'book': '1984', 'author': 'George Orwell'}),
                ('Nowadays people know the price of everything and the value of nothing.',
                 {'book': 'The Picture Of Dorian Gray', 'author': 'Oscar Wilde'})]


