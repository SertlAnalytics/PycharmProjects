"""
Description: This module contains all constants for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


class EL:  # entity labels
    COMPANY = 'COMPANY'
    PRODUCT = 'PRODUCT'
    OBJECT = 'OBJECT'
    TARGET_GROUP = 'TARGET_GROUP'
    MATERIAL = 'MATERIAL'

    @staticmethod
    def is_entity_label_tutti_relevant(ent_level: str) -> bool:
        return ent_level in [EL.PRODUCT, EL.COMPANY, EL.OBJECT, EL.TARGET_GROUP, EL.MATERIAL]


class SLCLS:  # css classes used within tutti sales
    OFFERS = '_2qT0v'
    MAIN_ANKER = '_16dGT'
    LOCATION = '_3f6Er'
    DATE = '_1kvIw'
    LINK = '_16dGT'  # or '_2SE_L'
    TITLE = '_2SE_L'
    DESCRIPTION = '_2c4Jo'
    PRICE = '_6HJe5'
    NUMBERS = '_1WJLw'


class SLSCLS:  # css classes used within tutti sale single
    OFFERS = '_142-1'
    MAIN_ANKER = '_16dGT'
    LOCATION_CLASS = '_35E6Q'  # _2ey_I'  # <div class="_35E6Q"><svg role="img" viewBox="0 0 35 35" class="svg-sprite"><use xlink:href="#canton-aargau"></use></svg><span class="_2ey_I">Aargau, 5430</span></div>
    LOCATION_SUB_CLASS = '_2ey_I'
    DATE_CLASS = '_2hsZ0'
    DATE_SUB_CLASS = '_3HMUQ'
    LINK = '_16dGT'  # or '_2SE_L'
    TITLE = '_36xB4'
    DESCRIPTION = ['_3E1vH', '_100oN', '_3MSKw']
    PRICE = '-zQvW'


class SCLS:  # css classes used within search offers
    FOUND_NUMBERS = '_35r2W'
    OFFERS = '_3aiCi'
    MAIN_ANKER = '_16dGT'
    LOCATION = '_3f6Er'
    DATE = '_1kvIw'
    LINK = '_16dGT'
    DESCRIPTION = '_2c4Jo'
    PRICE = '_6HJe5'
    NAVIGATION_MAIN = '_34zCr'
    NAVIGATION_ANCHOR = '_3bpXO _3vEQq'


class POS:
    ADJ = 'ADJ'  # adjective, e.g. 'warmes' (Innenfutter)
    ADP = 'ADP'  # AD, e.g. 'in', 'Dank'
    ADV = 'ADV'  # adverb, e.g. 'kaum' (gebraucht)
    CONJ = 'CONJ' # conjunction
    NUM = 'NUM'  # number, e.g. 37
    NOUN = 'NOUN'  # noun, e.g. 'Goretex'
    PART = 'PART'  # partical, e.g. 'zu' (verkaufen)
    PROPN = 'PROPN'  # proper noun, e.g. 'Wanderschuhe'
    PUNCT = 'PUNCT'  # punctuation, e.g. ','
    VERB = 'VERB'  # verb, e.g. 'verkaufen'
    X = 'X'         # X = ???

    @staticmethod
    def is_pos_noun(pos: str) -> bool:
        return pos in [POS.NOUN, POS.PROPN]


class TAG:
    ADJA = 'ADJA'  # ADJA??, e.g. 'warmes'
    ADJD = 'ADJD'  # ADJD??, e.g. 'einfach' (einfach höhenverstellbar)
    APPR = 'APPR'  # appr???, e.g. 'Dank' (Dank .. wasserdicht)
    CARD = 'CARD'  # Cardinal, e.g. 37
    NE = 'NE'  # NE??, e.g. 'Rufus', 'Lowa', 'Innenfutter', mostly POS=PROPN
    NN = 'NN'  # NN??, e.g. 'Rufus', 'Lowa', 'Innenfutter', mostly POS=NOUN
    VVFIN = 'VVFIN'  # VVFIN???, e.g. 'wasserdicht'
    VVPP = 'VVPP'  # VVPP??, e.g. 'gebraucht', 'erhalten'


class DEP:
    cj = 'cj'  # cj???, e.g. 'LOWA', mostly POS=NOUN or PROPN
    ROOT = 'ROOT'  # Root element, mostly POS=NOUN or PROPN
    pnc = 'pnc'  # punctuation, mostly POS=NOUN or PROPN
    punct = 'punct'  # punctuation, mostly POS=PUNKT
    subtok = 'subtok'  # subtoken (part of a larger token), e.g. 10 in '10-12' - head.text is the right neighbor
    nk = 'nk'  # nk = ????



