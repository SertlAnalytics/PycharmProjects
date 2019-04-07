"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from tutti_spacy import TuttiSpacy
from tutti_named_entity import TuttiCompanyEntity
from tutti_matcher import TuttiMatcher4IsNew, TuttiMatcher4IsUsed, TuttiMatcher4OriginalPrize, \
    TuttiMatcher4Size, TuttiMatcher4Number, TuttiMatcher4IsTotalPrice, TuttiMatcher4SinglePrize


class TC:
    TC_EXTENSIONS = 'TC_EXTENSIONS'
    TC_COMPANY_ENTITY = 'TC_COMPANY_ENTITY'
    TC_MATCHER_IS_NEW = 'TC_MATCHER_IS_NEW'
    TC_MATCHER_SIZE = 'TC_MATCHER_SIZE'
    TC_MATCHER_NUMBER = 'TC_MATCHER_NUMBER'
    TC_MATCHER_ORIGINAL_PRICE = 'TC_MATCHER_ORIGINAL_PRICE'
    TC_MATCHER_IS_USED = 'TC_MATCHER_IS_USED'
    TC_MATCHER_IS_TOTAL_PRICE = 'TC_MATCHER_IS_TOTAL_PRICE'
    TC_MATCHER_SINGLE_PRICE = 'TC_MATCHER_SINGLE_PRICE'


tc = TC.TC_MATCHER_IS_NEW

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
        'ist noch originalverpackt': True,
        'die Originalverpackung ist vorhanden': True,
        'der Tisch ist veraltet': False
    }
    matcher = TuttiMatcher4IsNew(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        is_new = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}'.format(key, value, is_new))
elif tc == TC.TC_MATCHER_IS_USED:
    test_value_dict = {
        'wenig gebraucht': True,
        'ist gut erhalten': True,
        'wie neu': False,
        'ist noch originalverpackt': False,
        'ein kleiner Schaden vorhanden': True,
        'die Flecken auf der Oberseite': True,
        'noch nicht gebraucht': True,
    }
    matcher = TuttiMatcher4IsUsed(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        # spacy.print_tokens_for_doc(doc)
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

elif tc == TC.TC_MATCHER_ORIGINAL_PRICE:
    test_value_dict = {
        'Rückenlehne verstellbar Neupreis 2300.- gestern': 2300,
        'Neupreis 1234.- 18 Stk vorhanden': 1234,
        'gekauft für 1000.- 18 Stk vorhanden': 1000,
        'CHF 245.- war Neupreis': 245,
        'Topstühle! NP: 2800.- 18 Stk vorhanden': 2800,
        'Topstühle! NP ca. 2900.- 18 Stk vorhanden': 2900,
    }
    matcher = TuttiMatcher4OriginalPrize(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        spacy.print_tokens_for_doc(doc)
        size = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}, result_ok: {}'.format(key, value, size, value == size))
elif tc == TC.TC_MATCHER_NUMBER:
    test_value_dict = {
        'Wie bieten an ein 2 er set': 2,
        'Preis für alle 34 Stück: 2000.-': 34,
        'es sind insgesamt 4 Stück': 4,
    }
    matcher = TuttiMatcher4Number(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        # spacy.print_tokens_for_doc(doc)
        size = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}, result_ok: {}'.format(key, value, size, value == size))
elif tc == TC.TC_MATCHER_SINGLE_PRICE:
    test_value_dict = {
        'Verkaufspreis 79.-': 79,
        'Preis pro Stück: 2000.-': 2000,
        'wir verkaufen auch einzeln für 79.- pro Stück': 79,
    }
    matcher = TuttiMatcher4SinglePrize(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        # spacy.print_tokens_for_doc(doc)
        size = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}, result_ok: {}'.format(key, value, size, value == size))
elif tc == TC.TC_MATCHER_IS_TOTAL_PRICE:
    test_value_dict = {
        "2'500 Fr. Preis für alle 4 Stühle zusammen": True,
        'Preis pro Stück: 2000.-': False,
        'Preis ist für 4 er Set': True,
        'Preis ist für 3 er set': True,
        'der Preis versteht sich als Gesamtpreis': True,
        'Der Preis ist für alle Stücke zusammen': True,
    }
    matcher = TuttiMatcher4IsTotalPrice(spacy.nlp)
    for key, value in test_value_dict.items():
        doc = spacy.nlp(key)
        # spacy.print_tokens_for_doc(doc)
        size = matcher.get_pattern_result_for_doc(doc)
        print('Test: {} - expected: {} - result: {}, result_ok: {}'.format(key, value, size, value == size))

else:
    company_entity = TuttiCompanyEntity()
    print(company_entity.get_entity_names_for_phrase_matcher())

