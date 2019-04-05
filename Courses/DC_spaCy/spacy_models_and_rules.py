"""
Description: This module is the course part for DataCamp spaCy Combining models and rules.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25

Introduction:
- this lesson is important to generalize your model

Statistical predictions vs. rules:
Use cases - statistical models: application need to generalize based on example,
        rule-based systems: dictionary with finite number of examples
Real world example - statistical models: product names, person names, subject/object relationship,
        rule-based systems: countries of the world, drug names, dog breeds
spaCy features: - statistical models: entity recognizer, dependency parser, part-of-speech tagger,
        rule-based systems: tokenizer, Matcher, PhraseMatcher

Efficient phrase matching:
- PhraseMatcher like regular expressions or keyword search - but with access to the tokens!
- Takes Doc object as patterns
- More efficient and faster than the Matcher
- Great for matching large word lists
"""

from spacy.tokens import Doc, Span
from spacy.matcher import Matcher, PhraseMatcher
from DC_spaCy.spacy_basics import SpacyCourseBase


class SpacyCourse4ModelsAndRules(SpacyCourseBase):
    def handle_word_vector(self):
        doc = self.nlp('I have a banana')
        # Access the vector via the token.vector attribute
        print(doc[3].vector)  # result: 300 dimensional vector of the word banana, but what does this mean?

    def handle_statistical_predictions(self):
        matcher = Matcher(self.nlp.vocab)
        pattern = [{'LOWER': 'golden'}, {'LOWER': 'retriever'}]
        matcher.add('DOG', None, pattern)
        doc = self.nlp('I have a Golden Retriever')
        for match_id, start, end in matcher(doc):
            span = doc[start:end]
            print('Matched span: {}'.format(span.text))
            # get the span's root token and root head token
            print('Root token: {}'.format(span.root.text))
            print('Root head token: {}'.format(span.root.head.text))
            print('Previous token: {} {}'.format(doc[start-1].text, doc[start-1].pos_))
        """
        Matched span: Golden Retriever
        Root token: Retriever
        Root head token: have
        Previous token: a DET
        """

    def handle_efficient_phrase_matching(self):
        matcher = PhraseMatcher(self.nlp.vocab)
        pattern = self.nlp('Golden Retriever')
        matcher.add('DOG', None, pattern)
        doc = self.nlp('I have a Golden Retriever')
        for match_id, start, end in matcher(doc):
            span = doc[start:end]
            print('Matched span: {}'.format(span.text))
            # get the span's root token and root head token
            print('Root token: {}'.format(span.root.text))
            print('Root head token: {}'.format(span.root.head.text))
            print('Previous token: {} {}'.format(doc[start - 1].text, doc[start - 1].pos_))
        """
        Matched span: Golden Retriever
        Root token: Retriever
        Root head token: have
        Previous token: a DET
        """

    def handle_countries_phrase_matching_with_pipeline(self):
        # Import the PhraseMatcher and initialize it
        doc = self.nlp('Czech Republic may help Slovakia protect its airspace.')
        matcher = PhraseMatcher(self.nlp.vocab)
        countries = ['Czech Republic', 'Australia', 'Germany', 'Slovakia']
        # Create pattern Doc objects and add them to the matcher
        # This is the faster version of: [nlp(country) for country in COUNTRIES]
        patterns = list(self.nlp.pipe(countries))
        matcher.add('COUNTRY', None, *patterns)

        # Call the matcher on the test document and print the result
        matches = matcher(doc)
        print([doc[start:end] for match_id, start, end in matches])




