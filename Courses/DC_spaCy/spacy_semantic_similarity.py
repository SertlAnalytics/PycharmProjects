"""
Description: This module is the course part for DataCamp spaCy data structures.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25

Content:
- spaCy can compare two objects and predict similarity (doc, token, span)
- these objects have a similarity() method - output: float between 0 and 1

Important: For this you need a larger model which has word vectors included, e.g. en_core_web_md (medium model)
or en_core_web_lg (large model) NOT the small one

How does spaCy predict similarity?
- Similarity is determined using word vectors
- Multi-dimensional meaning representations of words
- Generated using an alorithm like Word2Vec and lots of text
- Can be added to spaCy's statistical models
- default: cosine similarity, but can be adjusted
- Doc and Span: vectors default to average of token vectors
- Short phrases are better than long documents with many irrelevant words

Similarity depends on the application context:
- useful for many applications: recommendation systems, flagging duplicates, etc.
- but: there is no objective definition of "similarity"
- it depends on the context and what application needs to do
"""

from spacy.tokens import Doc, Span
from DC_spaCy.spacy_basics import SpacyCourseBase


class SpacyCourse4SemanticSimilarity(SpacyCourseBase):
    def handle_word_vector(self):
        doc = self.nlp('I have a banana')
        # Access the vector via the token.vector attribute
        print(doc[3].vector)  # result: 300 dimensional vector of the word banana, but what does this mean?

    def handle_strange_similarity_example(self):
        doc_1 = self.nlp('I like cats')
        doc_2 = self.nlp('I hate cats')
        self.__print_similarity__(doc_1, doc_2)

    def handle_similarity(self):
        # compare two documents
        doc1 = self.nlp('I like fast food')
        doc2 = self.nlp('I like pizza')
        self.__print_similarity__(doc1, doc2)

        # compare two tokens
        doc = self.nlp('I like pizza and pasta')
        token1 = doc[2]
        token2 = doc[4]
        self.__print_similarity__(token1, token2)

        # compare different types of objects
        doc = self.nlp('I like pizza')
        token = self.nlp('soap')[0]
        self.__print_similarity__(doc, token)

        # compare a span with a doc
        span = self.nlp('I like pizza and pasta')[2:5]
        doc = self.nlp('McDonalds sells burgers')
        self.__print_similarity__(span, doc)

    @staticmethod
    def __print_similarity__(obj_1, obj_2):
        similarity = obj_1.similarity(obj_2)
        similarity_text = SpacyCourse4SemanticSimilarity.__get_similarity_text__(similarity)
        print("\nSimilarity between '{}' and '{}': {:.2f} ({})".format(
            obj_1.text, obj_2.text, similarity, similarity_text))

    @staticmethod
    def __get_similarity_text__(similarity: float):
        if similarity >= 0.9:
            return 'nearly identical'
        elif similarity >= 0.75:
            return 'very similar'
        elif similarity >= 0.65:
            return 'similar'
        elif similarity >= 0.45:
            return 'indifferent'
        return 'not similar'
