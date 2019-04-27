"""
Description: This module is the base class for our Tutti nlp (based on the original spaCy.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher
from tutti_constants import EL
from tutti_named_entity import TuttiEntityHandler
from tutti_named_entity import TuttiCompanyEntity, TuttiProductEntity, TuttiObjectTypeEntity
from matcher.tutti_matcher_4_is_new import TuttiMatcher4IsNew
from matcher.tutti_matcher_4_is_used import TuttiMatcher4IsUsed
from matcher.tutti_matcher_4_original_price import TuttiMatcher4OriginalPrize
from matcher.tutti_matcher_4_size import TuttiMatcher4Size
from matcher.tutti_matcher_4_number import TuttiMatcher4Number
from matcher.tutti_matcher_4_is_total_price import TuttiMatcher4IsTotalPrice
from matcher.tutti_matcher_4_single_prize import TuttiMatcher4SinglePrize
import spacy


class CustomTokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, text: str):
        text = self.__replace_substrings__(text)
        return self.tokenizer(text)

    def __replace_substrings__(self, text: str) -> str:
        for replacement_string in self.replacement_dict:
            if text.find(replacement_string) > -1:
                text = text.replace(replacement_string, self.replacement_dict[replacement_string])
        return text

    @property
    def replacement_dict(self) -> dict:
        return {
            'Fr.': 'CHF',
            ',--': '.-',
            ',-': '.-',
            '.--': '.-',
        }


class WhitespaceTokenizer(object):  # see https://spacy.io/usage/linguistic-features#entity-types
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        text = text.replace(',--', '.-')
        words = text.split(' ')
        # All tokens 'own' a subsequent space character in this tokenizer
        spaces = [True] * len(words)
        return Doc(self.vocab, words=words, spaces=spaces)


class TuttiSpacy:
    def __init__(self, load_sm=True):
        self._load_sm = load_sm
        self._nlp = spacy.load('de_core_news_sm') if load_sm else spacy.load('de_core_news_md')
        self._nlp.tokenizer = CustomTokenizer(self._nlp.tokenizer)
        # self._nlp.tokenizer = WhitespaceTokenizer(self._nlp.vocab)
        self._matcher_company = self.__get_matcher_for_entity_type__(EL.COMPANY)
        self._matcher_product = self.__get_matcher_for_entity_type__(EL.PRODUCT)
        self._matcher_object = self.__get_matcher_for_entity_type__(EL.OBJECT)
        self._matcher_target_group = self.__get_matcher_for_entity_type__(EL.TARGET_GROUP)
        # self._nlp.add_pipe(self.replacement_component, name='CUSTOM_REPLACEMENT', before='tagger')
        self._nlp.add_pipe(self.company_component, name='CUSTOM_COMPANY', after='ner')
        self._nlp.add_pipe(self.product_component, name='CUSTOM_PRODUCT', after='CUSTOM_COMPANY')
        self._nlp.add_pipe(self.object_component, name='CUSTOM_OBJECT', after='CUSTOM_PRODUCT')
        self._nlp.add_pipe(self.object_target_group, name='CUSTOM_TARGET_GROUP', after='CUSTOM_OBJECT')
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
        entity_names = TuttiEntityHandler.get_entity_names_for_entity_label(entity_type)
        patterns = list(self.nlp.pipe(entity_names))
        matcher.add(entity_type, None, *patterns)
        return matcher

    def replacement_component(self, doc):  # ToDo see https://nlpforhackers.io/complete-guide-to-spacy/
        doc.text = doc.text.replace(',--', '.-')
        return doc

    def company_component(self, doc):
        matches = self._matcher_company(doc)
        spans = [Span(doc, start, end, label=EL.COMPANY) for match_id, start, end in matches]
        doc.ents = spans  # Overwrite the doc.ents with the matched spans
        return doc

    def product_component(self, doc):
        matches = self._matcher_product(doc)
        spans = [Span(doc, start, end, label=EL.PRODUCT) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def object_component(self, doc):
        matches = self._matcher_object(doc)
        spans = [Span(doc, start, end, label=EL.OBJECT) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def object_target_group(self, doc):
        matches = self._matcher_target_group(doc)
        spans = [Span(doc, start, end, label=EL.TARGET_GROUP) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def __get_doc_with_added_span_list_as_entities__(self, doc: Doc, spans: list):
        try:
            doc.ents = list(doc.ents) + spans  # Overwrite the doc.ents with the matched spans
        except ValueError:
            print('Error with span: {} - already as entity available.'.format(spans))
            self.print_tokens_for_doc(doc)
        finally:
            return doc

    @staticmethod
    def print_tokens_for_doc(doc: Doc):
        for token in doc:
            print('token.text={}, token.lemma_={}, pos_={}, dep_={}, head.text={}, ent_type_={}'.format(
                token.text, token.lemma_, token.pos_, token.dep_, token.head.text, token.ent_type_))

    @staticmethod
    def print_text_for_doc(doc: Doc):
        print(doc.text)

    @staticmethod
    def print_entities_for_doc(doc: Doc):
        for ent in doc.ents:
            print('ent.text={}, ent.label_={}'.format(ent.text, ent.label_))

    def __set_doc_extensions__(self): # Register some Doc property extensions
        Doc.set_extension('get_size', getter=self.__get_size__)
        Doc.set_extension('get_single_price', getter=self.__get_single_price__)
        Doc.set_extension('get_number', getter=self.__get_number__)
        Doc.set_extension('get_original_price', getter=self.__get_original_price__)
        Doc.set_extension('is_new', getter=self.__is_new__)
        Doc.set_extension('is_used', getter=self.__is_used__)
        Doc.set_extension('is_total_price', getter=self.__is_total_price__)

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

    def __is_total_price__(self, doc):
        return TuttiMatcher4IsTotalPrice(self._nlp).get_pattern_result_for_doc(doc)

    def __get_single_price__(self, doc):
        return TuttiMatcher4SinglePrize(self._nlp).get_pattern_result_for_doc(doc)


