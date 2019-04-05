"""
Description: This module is the beginners course for DataCamp spaCy for finding words phrases, names and concepts
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25
"""


from spacy.lang.en import English
from spacy.lang.de import German
from spacy.tokens import Doc
import spacy  # python -m spacy download en_core_web_sm


class SCYL:  # spaCy lessons
    MATCHER_PATTERN = 'MATCHER_PATTERN'
    VOCAB_LEXEMES_STRING_STORE = 'VOCAB_LEXEMES_STRING_STORE'
    DOC_SPAN_TOKEN = 'DOC_SPAN_TOKEN'
    WORD_VECTORS = 'WORD_VECTORS'
    SEMANTIC_SIMILARITY = 'SEMANTIC_SIMILARITY'
    MODELS_RULES = 'MODELS_RULES'
    PIPELINE = 'PIPELINE'
    SCALING = 'SCALING'
    TRAINING = 'TRAINING'


class SpacyCourseBase:
    def __init__(self, model='', blank_model=''):
        self._model = model
        self._blank_model = blank_model
        self.nlp = self.__get_nlp__()

    def __get_nlp__(self):
        if self._blank_model != '':  # i.e. the pipeline has only the tokenizer, all other pipes have to added manually
            return spacy.blank(self._blank_model)
        if self._model == 'en':
            return English()
        elif self._model == 'de':
            return German()
        else:
            return spacy.load('en_core_web_sm') if self._model == '' else spacy.load(self._model)

    @staticmethod
    def __print_tokens_for_doc__(doc: Doc):
        for token in doc:
            print('token.text={}, pos_={}, dep_={}, head.text={}'.format(
                token.text, token.pos_, token.dep_, token.head.text))

    @staticmethod
    def __print_text_for_doc__(doc: Doc):
        print(doc.text)

    @staticmethod
    def __print_entities_for_doc__(doc: Doc):
        for ent in doc.ents:
            print('ent.text={}, ent.label_={}'.format(ent.text, ent.label_))

    def find_a_verb_after_a_proper_noun(self, doc: Doc):
        # Get all tokens and part-of-speech tags
        for token in doc:
            # Check if the current token is a proper noun
            if token.pos_ == 'PROPN' and token.i < len(doc):
                # Check if the next token is a verb
                token_next = doc[token.i + 1]
                if token_next.pos_ == 'VERB':
                    print('Found a verb after a proper noun!: {} {}'.format(token.text, token_next.text))

    def exercise_01(self):
        # Process the text
        doc = self.nlp("I like tree kangaroos and narwhals.")
        # A slice of the Doc for "tree kangaroos"
        tree_kangaroos = doc[2:4]
        print(tree_kangaroos.text)
        # A slice of the Doc for "tree kangaroos and narwhals" (without the ".")
        tree_kangaroos_and_narwhals = doc[2:6]
        print(tree_kangaroos_and_narwhals.text)

    def exercise_02(self):
        # Process the text
        doc = self.nlp("In 1990, more than 60% of people in East Asia were in extreme poverty. Now less than 4% are.")
        # Iterate over the tokens in the doc
        for token in doc:
            # Check if the token resembles a number
            if token.like_num:
                # Get the next token in the document
                next_token = doc[token.i + 1]
                # Check if the next token's text equals '%'
                if next_token.text == '%':
                    print('Percentage found:', token.text)

    def predicting_part_of_speach(self):  # pos_
        doc = self.nlp('She ate the pizza')
        for token in doc:
            print(token.text, token.pos_)
        """
        She PRON
        ate VERB
        the DET
        pizza NOUN
        """

    def predicting_syntactical_dependencies(self):  # dep_
        doc = self.nlp('Apple is looking at buying U.K. startup for $1 billion')
        for token in doc:
            print(token.text, token.pos_, token.dep_, token.head.text)
        """
        She PRON nsubj ate      # nsubj = nominal subject
        ate VERB ROOT ate       # ROOT = ???
        the DET det pizza       # det = determines (article)
        pizza NOUN dobj ate     # dobj = direct object
        """

    def predicting_named_entities(self):
        doc = self.nlp('Apple is looking at buying U.K. startup for $1 billion')
        print(doc.text)  # Print the document text
        for ent in doc.ents:
            print(ent.text, ent.label_)
        """
        Apple ORG
        U.K. GPE
        $1 billion MONEY
        """

    def excercise_pos_dep(self):
        text = "It’s official: Apple is the first U.S. public company to reach a $1 trillion market value"

        # Process the text
        doc = self.nlp(text)

        for token in doc:
            # Get the token text, part-of-speech tag and dependency label
            token_text = token.text
            token_pos = token.pos_
            token_dep = token.dep_
            # This is for formatting only
            print('{:<12}{:<10}{:<10}'.format(token_text, token_pos, token_dep))

    def explain(self, term: str):
        # example term = GPE = Countries, cities, states,
        # MONEY = Monetary values, including unit
        print(spacy.explain(term))


# course = SpacyCourseBase()
# # course.exercise_01()
# # course.exercise_02()
# course.predicting_named_entities()
# course.explain('MONEY')
# course.explain('POS')
# course.explain('GPE')



