"""
Description: This module is the base class for our Tutti nlp (based on the original spaCy.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher
from salesman_tutti.tutti_constants import EL, POS
from entities.salesman_named_entity import SalesmanEntityHandler
from matcher.tutti_matcher_4_is_new import TuttiMatcher4IsNew
from matcher.tutti_matcher_4_is_like_new import TuttiMatcher4IsLikeNew
from matcher.tutti_matcher_4_is_used import TuttiMatcher4IsUsed
from matcher.tutti_matcher_4_original_price import TuttiMatcher4PriceOriginal
from matcher.tutti_matcher_4_size import TuttiMatcher4Size
from matcher.tutti_matcher_4_number import TuttiMatcher4Number
from matcher.tutti_matcher_4_is_total_price import TuttiMatcher4IsTotalPrice
from matcher.tutti_matcher_4_single_prize import TuttiMatcher4PriceSingle
from matcher.tutti_matcher_4_cover_available import TuttiMatcher4CoverAvailable
from matcher.tutti_matcher_4_age import TuttiMatcher4Age
from matcher.tutti_matcher_4_warranty import TuttiMatcher4Warranty
import spacy


class CustomTokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, text: str):
        text = self.__replace_substrings__(text)
        return self.tokenizer(text)

    def __replace_substrings__(self, text: str) -> str:
        for replacement_string in self.replacement_dict:
            string_new = self.replacement_dict[replacement_string]
            repl_list = [replacement_string.lower(), replacement_string.upper(), replacement_string.capitalize()]
            for repl_string in repl_list:
                if text.find(repl_string) != -1:
                    text = text.replace(repl_string, string_new)
                    break
        return text

    @property
    def replacement_dict(self) -> dict:
        return {
            'Fr.': 'CHF',
            ',--': '.-',
            ',-': '.-',
            '.--': '.-',
            'Huawai': 'Huawei',
            'Schalfsack': 'Schlafsack',
            'Kommunionskleid': 'Kommunionkleid',
            'Stoßstange': 'Stossstange',
            'WIFI': 'WiFi',
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


class SalesmanSpacy:
    def __init__(self, load_sm=True):
        self._load_sm = load_sm
        self._nlp = spacy.load('de_core_news_sm') if load_sm else spacy.load('de_core_news_md')
        self._nlp.tokenizer = CustomTokenizer(self._nlp.tokenizer)
        # self._nlp.tokenizer = WhitespaceTokenizer(self._nlp.vocab)
        self._matcher_company = self.__get_matcher_for_entity_type__(EL.COMPANY)
        self._matcher_product = self.__get_matcher_for_entity_type__(EL.PRODUCT)
        self._matcher_object = self.__get_matcher_for_entity_type__(EL.OBJECT)
        self._matcher_target_group = self.__get_matcher_for_entity_type__(EL.TARGET_GROUP)
        self._matcher_material = self.__get_matcher_for_entity_type__(EL.MATERIAL)
        self._matcher_technology = self.__get_matcher_for_entity_type__(EL.TECHNOLOGY)
        # self._nlp.add_pipe(self.replacement_component, name='CUSTOM_REPLACEMENT', before='tagger')
        self._nlp.add_pipe(self.company_component, name='CUSTOM_COMPANY', after='ner')
        self._nlp.add_pipe(self.product_component, name='CUSTOM_PRODUCT', after='CUSTOM_COMPANY')
        self._nlp.add_pipe(self.object_component, name='CUSTOM_OBJECT', after='CUSTOM_PRODUCT')
        self._nlp.add_pipe(self.target_group_component, name='CUSTOM_TARGET_GROUP', after='CUSTOM_OBJECT')
        self._nlp.add_pipe(self.material_component, name='CUSTOM_MATERIAL', after='CUSTOM_TARGET_GROUP')
        self._nlp.add_pipe(self.technology_component, name='CUSTOM_TECHNOLOGY', after='CUSTOM_MATERIAL')
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
        entity_names = SalesmanEntityHandler.get_entity_names_for_entity_label(entity_type)
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

    def material_component(self, doc):
        matches = self._matcher_material(doc)
        spans = [Span(doc, start, end, label=EL.MATERIAL) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def technology_component(self, doc):
        matches = self._matcher_technology(doc)
        spans = [Span(doc, start, end, label=EL.TECHNOLOGY) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def product_component(self, doc):
        matches = self._matcher_product(doc)
        spans = [Span(doc, start, end, label=EL.PRODUCT) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def object_component(self, doc):
        matches = self._matcher_object(doc)
        spans = [Span(doc, start, end, label=EL.OBJECT) for match_id, start, end in matches]
        return self.__get_doc_with_added_span_list_as_entities__(doc, spans)

    def target_group_component(self, doc):
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
        Doc.set_extension('size', getter=self.__get_size__)
        Doc.set_extension('price_single', getter=self.__get_price_single__)
        Doc.set_extension('number', getter=self.__get_number__)
        Doc.set_extension('first_pos_number', getter=self.__get_fist_pos_number__)
        Doc.set_extension('price_original', getter=self.__get_price_original__)
        Doc.set_extension('is_new', getter=self.__is_new__)
        Doc.set_extension('is_like_new', getter=self.__is_like_new__)
        Doc.set_extension('is_used', getter=self.__is_used__)
        Doc.set_extension('is_total_price', getter=self.__is_total_price__)
        Doc.set_extension('is_cover_available', getter=self.__is_cover_available__)
        Doc.set_extension('age', getter=self.__get_age__)
        Doc.set_extension('warranty', getter=self.__get_warranty__)

    def __get_size__(self, doc):
        return TuttiMatcher4Size(self._nlp).get_pattern_result_for_doc(doc)

    def __get_age__(self, doc):
        return TuttiMatcher4Age(self._nlp).get_pattern_result_for_doc(doc)

    def __get_number__(self, doc):
        return TuttiMatcher4Number(self._nlp).get_pattern_result_for_doc(doc)

    @staticmethod
    def __get_fist_pos_number__(doc):
        for token in doc:
            if token.pos_ == POS.NUM:
                if token.text.isnumeric():
                    return int(token.text)

    def __get_price_original__(self, doc):
        return TuttiMatcher4PriceOriginal(self._nlp).get_pattern_result_for_doc(doc)

    def __is_new__(self, doc):
        return TuttiMatcher4IsNew(self._nlp).get_pattern_result_for_doc(doc)

    def __is_like_new__(self, doc):
        return TuttiMatcher4IsLikeNew(self._nlp).get_pattern_result_for_doc(doc)

    def __is_used__(self, doc):
        return TuttiMatcher4IsUsed(self._nlp).get_pattern_result_for_doc(doc)

    def __is_total_price__(self, doc):
        return TuttiMatcher4IsTotalPrice(self._nlp).get_pattern_result_for_doc(doc)

    def __get_price_single__(self, doc):
        return TuttiMatcher4PriceSingle(self._nlp).get_pattern_result_for_doc(doc)

    def __is_cover_available__(self, doc):
        return TuttiMatcher4CoverAvailable(self._nlp).get_pattern_result_for_doc(doc)

    def __get_warranty__(self, doc):
        return TuttiMatcher4Warranty(self._nlp).get_pattern_result_for_doc(doc)


