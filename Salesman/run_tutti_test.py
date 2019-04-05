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


class TC:
    TC_EXTENSIONS = 'TC Extensions'
    TC_COMPANY_ENTITY = 'TC Company Entity'


tc = TC.TC_EXTENSIONS

if tc == TC.TC_EXTENSIONS:
    text = 'Wanderschuhe, Lowa, Rufus III GTX, Gr. 37, Goretex, eames, Mercedes Benz, eames alu chair, ' \
           'Masse: 175x75x74. Farbe: Weiss. '

    spacy = TuttiSpacy()
    doc = spacy.nlp(text)
    spacy.print_tokens_for_doc(doc)
    print('doc._.size={}'.format(doc._.get_size))
    print('doc._.is_new={}'.format(doc._.is_new))
    print('doc._.is_used={}'.format(doc._.is_used))
# spacy.print_tokens_for_doc(doc)
# spacy.print_entities_for_doc(doc)
else:
    company_entity = TuttiCompanyEntity()
    print(company_entity.get_entity_names_for_phrase_matcher())

