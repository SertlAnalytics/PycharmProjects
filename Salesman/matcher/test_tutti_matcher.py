"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_nlp.salesman_spacy import SalesmanSpacy
from entities.salesman_named_entity import CompanyEntity
from matcher.tutti_matcher_4_is_new import TuttiMatcher4IsNew
from matcher.tutti_matcher_4_is_used import TuttiMatcher4IsUsed
from matcher.tutti_matcher_4_original_price import TuttiMatcher4PriceOriginal
from matcher.tutti_matcher_4_size import TuttiMatcher4Size
from matcher.tutti_matcher_4_number import TuttiMatcher4Number
from matcher.tutti_matcher_4_is_total_price import TuttiMatcher4IsTotalPrice
from matcher.tutti_matcher_4_single_prize import TuttiMatcher4PriceSingle
from matcher.tutti_matcher_4_is_like_new import TuttiMatcher4IsLikeNew
from matcher.tutti_matcher_4_cover_available import TuttiMatcher4CoverAvailable
from matcher.tutti_matcher_4_age import TuttiMatcher4Age
from matcher.tutti_matcher_4_warranty import TuttiMatcher4Warranty


class TC:
    TC_COMPANY_ENTITY = 'TC_COMPANY_ENTITY'
    TC_MATCHER_IS_NEW = 'TC_MATCHER_IS_NEW'
    TC_MATCHER_IS_LIKE_NEW = 'TC_MATCHER_IS_LIKE_NEW'
    TC_MATCHER_SIZE = 'TC_MATCHER_SIZE'
    TC_MATCHER_NUMBER = 'TC_MATCHER_NUMBER'
    TC_MATCHER_ORIGINAL_PRICE = 'TC_MATCHER_ORIGINAL_PRICE'
    TC_MATCHER_IS_USED = 'TC_MATCHER_IS_USED'
    TC_MATCHER_IS_TOTAL_PRICE = 'TC_MATCHER_IS_TOTAL_PRICE'
    TC_MATCHER_SINGLE_PRICE = 'TC_MATCHER_SINGLE_PRICE'
    TC_MATCHER_COVER_AVAILABLE = 'TC_MATCHER_COVER_AVAILABLE'
    TC_MATCHER_AGE = 'TC_MATCHER_AGE'
    TC_MATCHER_WARRANTY = 'TC_MATCHER_WARRANTY'


tc = TC.TC_MATCHER_NUMBER

spacy = SalesmanSpacy()

if tc == TC.TC_MATCHER_IS_NEW:
    matcher = TuttiMatcher4IsNew(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_IS_LIKE_NEW:
    matcher = TuttiMatcher4IsLikeNew(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_IS_USED:
    matcher = TuttiMatcher4IsUsed(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_SIZE:
    matcher = TuttiMatcher4Size(spacy.nlp)
    matcher.run_test(spacy, True)
elif tc == TC.TC_MATCHER_ORIGINAL_PRICE:
    matcher = TuttiMatcher4PriceOriginal(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_NUMBER:
    matcher = TuttiMatcher4Number(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_SINGLE_PRICE:
    matcher = TuttiMatcher4PriceSingle(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_IS_TOTAL_PRICE:
    matcher = TuttiMatcher4IsTotalPrice(spacy.nlp)
    matcher.run_test(spacy, True)
elif tc == TC.TC_MATCHER_COVER_AVAILABLE:
    matcher = TuttiMatcher4CoverAvailable(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_AGE:
    matcher = TuttiMatcher4Age(spacy.nlp)
    matcher.run_test(spacy, False)
elif tc == TC.TC_MATCHER_WARRANTY:
    matcher = TuttiMatcher4Warranty(spacy.nlp)
    matcher.run_test(spacy, True)
else:
    company_entity = CompanyEntity()
    print(company_entity.get_entity_names_for_phrase_matcher())

