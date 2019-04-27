"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from tutti_spacy import TuttiSpacy
from tutti_named_entity import TuttiCompanyEntity
from matcher.tutti_matcher_4_is_new import TuttiMatcher4IsNew
from matcher.tutti_matcher_4_is_used import TuttiMatcher4IsUsed
from matcher.tutti_matcher_4_original_price import TuttiMatcher4OriginalPrize
from matcher.tutti_matcher_4_size import TuttiMatcher4Size
from matcher.tutti_matcher_4_number import TuttiMatcher4Number
from matcher.tutti_matcher_4_is_total_price import TuttiMatcher4IsTotalPrice
from matcher.tutti_matcher_4_single_prize import TuttiMatcher4SinglePrize


class TC:
    TC_COMPANY_ENTITY = 'TC_COMPANY_ENTITY'
    TC_MATCHER_IS_NEW = 'TC_MATCHER_IS_NEW'
    TC_MATCHER_SIZE = 'TC_MATCHER_SIZE'
    TC_MATCHER_NUMBER = 'TC_MATCHER_NUMBER'
    TC_MATCHER_ORIGINAL_PRICE = 'TC_MATCHER_ORIGINAL_PRICE'
    TC_MATCHER_IS_USED = 'TC_MATCHER_IS_USED'
    TC_MATCHER_IS_TOTAL_PRICE = 'TC_MATCHER_IS_TOTAL_PRICE'
    TC_MATCHER_SINGLE_PRICE = 'TC_MATCHER_SINGLE_PRICE'


tc = TC.TC_MATCHER_ORIGINAL_PRICE

spacy = TuttiSpacy()

if tc == TC.TC_MATCHER_IS_NEW:
    matcher = TuttiMatcher4IsNew(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_IS_USED:
    matcher = TuttiMatcher4IsUsed(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_SIZE:
    matcher = TuttiMatcher4Size(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_ORIGINAL_PRICE:
    matcher = TuttiMatcher4OriginalPrize(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_NUMBER:
    matcher = TuttiMatcher4Number(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_SINGLE_PRICE:
    matcher = TuttiMatcher4SinglePrize(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_IS_TOTAL_PRICE:
    matcher = TuttiMatcher4IsTotalPrice(spacy.nlp)
    matcher.run_test(spacy, False)
else:
    company_entity = TuttiCompanyEntity()
    print(company_entity.get_entity_names_for_phrase_matcher())

