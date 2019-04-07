"""
Description: This module is the base class for our Tutti nlp (based on the original spaCy.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from spacy import displacy
from spacy.tokens import Doc, Span
from spacy.matcher import Matcher, PhraseMatcher
from tutti_constants import EL, POS
from tutti_named_entity import TuttiCompanyEntity, TuttiProductEntity
from tutti_matcher import TuttiMatcher4IsNew, TuttiMatcher4IsUsed, TuttiMatcher4OriginalPrize, \
    TuttiMatcher4Size, TuttiMatcher4Number
import spacy


class TuttiSpacy:
    def __init__(self, load_sm=True):
        self._load_sm = load_sm
        self._nlp = spacy.load('de_core_news_sm') if load_sm else spacy.load('de_core_news_md')
        self._matcher_company = self.__get_matcher_for_entity_type__(EL.COMPANY)
        self._matcher_product = self.__get_matcher_for_entity_type__(EL.PRODUCT)
        self._nlp.add_pipe(self.company_component, name='CUSTOM_COMPANY', after='ner')
        self._nlp.add_pipe(self.product_component, name='CUSTOM_PRODUCT', after='CUSTOM_COMPANY')
        self.__set_doc_extensions__()

    @property
    def nlp(self):
        return self._nlp

    @property
    def sm_loaded(self):
        return self._load_sm

    @staticmethod
    def get_similarity_text(similarity: float):
        if similarity >= 0.9:
            return 'nearly identical'
        elif similarity >= 0.75:
            return 'very similar'
        elif similarity >= 0.65:
            return 'similar'
        elif similarity >= 0.45:
            return 'indifferent'
        return 'not similar'

    def __get_matcher_for_entity_type__(self, entity_type: str):
        matcher = PhraseMatcher(self.nlp.vocab)
        if entity_type == EL.COMPANY:
            entity_names = TuttiCompanyEntity().get_entity_names_for_phrase_matcher()
        else:
            entity_names = TuttiProductEntity().get_entity_names_for_phrase_matcher()
        patterns = list(self.nlp.pipe(entity_names))
        matcher.add(entity_type, None, *patterns)
        return matcher

    def company_component(self, doc):
        matches = self._matcher_company(doc)
        spans = [Span(doc, start, end, label=EL.COMPANY) for match_id, start, end in matches]
        doc.ents = spans  # Overwrite the doc.ents with the matched spans
        return doc

    def product_component(self, doc):
        matches = self._matcher_product(doc)
        spans = [Span(doc, start, end, label=EL.PRODUCT) for match_id, start, end in matches]
        doc.ents = list(doc.ents) + spans  # Overwrite the doc.ents with the matched spans
        return doc

    @staticmethod
    def print_tokens_for_doc(doc: Doc):
        for token in doc:
            print('token.text={}, token.lemma_={}, pos_={}, dep_={}, head.text={}'.format(
                token.text, token.lemma_, token.pos_, token.dep_, token.head.text))

    @staticmethod
    def print_text_for_doc(doc: Doc):
        print(doc.text)

    @staticmethod
    def print_entities_for_doc(doc: Doc):
        for ent in doc.ents:
            print('ent.text={}, ent.label_={}'.format(ent.text, ent.label_))

    def __set_doc_extensions__(self): # Register some Doc property extensions
        Doc.set_extension('get_size', getter=self.__get_size__)
        Doc.set_extension('get_number', getter=self.__get_number__)
        Doc.set_extension('get_original_price', getter=self.__get_original_price__)
        Doc.set_extension('is_new', getter=self.__is_new__)
        Doc.set_extension('is_used', getter=self.__is_used__)

    def __get_size__(self, doc):
        return TuttiMatcher4Size(self._nlp).get_pattern_result_for_doc(doc)

    def __get_number__(self, doc):
        return TuttiMatcher4Number(self._nlp).get_pattern_result_for_doc(doc)

    def __get_original_price__(self, doc):
        return TuttiMatcher4OriginalPrize(self._nlp).get_pattern_result_for_doc(doc)

    def __is_new__(self, doc):
        return TuttiMatcher4IsNew(self._nlp).get_pattern_result_for_doc(doc)

    def __is_used__(self, doc):
        return TuttiMatcher4IsUsed(self._nlp).get_pattern_result_for_doc(doc)

