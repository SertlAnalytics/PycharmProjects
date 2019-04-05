"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.myprofiler import MyProfiler
from tutti import Tutti
from time import sleep
from tutti_spacy import TuttiSpacy
from tutti_named_entity import TuttiCompanyEntity, TuttiProductEntity
from tutti_matcher import TuttiMatcher4IsNew, TuttiMatcher4IsUsed, TuttiMatcher4OriginalPrize, TuttiMatcher4Size


class TC:
    TC_EXTENSIONS = 'TC Extensions'
    TC_COMPANY_ENTITY = 'TC Company Entity'
    TC_MATCHER_IS_NEW = 'TC_MATCHER_IS_NEW'
    TC_MATCHER_SIZE = 'TC_MATCHER_SIZE'


tc = TC.TC_MATCHER_SIZE

spacy = TuttiSpacy()

if tc == TC.TC_EXTENSIONS:
    text = 'Wanderschuhe, Lowa, Rufus III GTX, Gr. 37, Goretex, eames, Mercedes Benz, eames alu chair, ' \
           'Masse: Durchmesser 90 cm'
    doc = spacy.nlp(text)
    spacy.print_tokens_for_doc(doc)
    print('doc._.size={}'.format(doc._.get_size))
    print('doc._.is_new={}'.format(doc._.is_new))
    print('doc._.is_used={}'.format(doc._.is_used))
# spacy.print_tokens_for_doc(doc)
# spacy.print_entities_for_doc(doc)
elif tc == TC.TC_MATCHER_IS_NEW:
    test_value_dict = {
        'ist neuwertig': True,
        'Ich verkaufe meine neuwertigen Damen Wanderschuhe': True,
        'Weisser USM Haller Tisch in neuwertigem Zustand': True,
        'der Tisch ist neu': True,
        'der Tisch ist wie neu': True,
        'Zustand: sehr gut': True,
        'der Tisch ist in sehr gutem Zustand': True,
        'der Tisch ist veraltet': False
    }
    matcher = TuttiMatcher4IsNew(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        is_new = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}'.format(key, value, is_new))
elif tc == TC.TC_MATCHER_SIZE:
    test_value_dict = {
        'Gr. 37': '37',
        'Grösse 38': '38',
        'Masse: Durchmesser 90 cm': 'Durchmesser 90 cm',
        'Masse: 175x100x74 cm': '175x100x74 cm',
        '175x100x74 cm': '175x100x74 cm'
    }
    matcher = TuttiMatcher4Size(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        size = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}, result_ok: {}'.format(key, value, size, value == size))
else:
    company_entity = TuttiCompanyEntity()
    print(company_entity.get_entity_names_for_phrase_matcher())

