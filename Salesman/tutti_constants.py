"""
Description: This module contains all constants for Tutti
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""


class EL:  # entity labels
    COMPANY = 'COMPANY'
    PRODUCT = 'PRODUCT'

    @staticmethod
    def is_entity_label_tutti_relevant(ent_level: str) -> bool:
        return ent_level in [EL.PRODUCT, EL.COMPANY]


class TC:  # Tutti columns
    ID = 'ID'
    ID_MASTER = 'ID master'
    HREF = 'Link'
    DATE = 'Date'
    LOCATION = 'Location'
    STATE = 'State'
    TITLE = 'Title'
    DESCRIPTION = 'Description'
    PRICE = 'Price'
    PRICE_ORIGINAL = 'Price (orig.)'
    SIZE = 'Size'
    NUMBER = 'Number'
    IS_NEW = 'Is new'
    IS_USED = 'Is used'
    VISITS = 'Visits'
    BOOK_MARKS = 'Bookmarks'
    SEARCH_LABELS = 'Search labels'
    ENTITY_LABELS = 'Entity labels'
    FOUND_BY_LABELS = 'Found by labels'

    @staticmethod
    def get_columns_for_virtual_offers_in_file():
        return [TC.TITLE, TC.DESCRIPTION, TC.PRICE]

    @staticmethod
    def get_columns_for_excel():
        return [TC.ID, TC.ID_MASTER, TC.DATE, TC.LOCATION, TC.STATE,
                TC.PRICE, TC.PRICE_ORIGINAL, TC.NUMBER, TC.SIZE,
                TC.TITLE, TC.DESCRIPTION,
                TC.IS_NEW, TC.IS_USED, TC.VISITS, TC.BOOK_MARKS,
                TC.SEARCH_LABELS, TC.ENTITY_LABELS, TC.FOUND_BY_LABELS, TC.HREF]


class OCLS:  # css classes used within offers
    OFFERS = '_2qT0v'
    MAIN_ANKER = '_16dGT'
    LOCATION = '_3f6Er'
    DATE = '_1kvIw'
    LINK = '_16dGT'
    DESCRIPTION = '_2c4Jo'
    PRICE = '_6HJe5'
    NUMBERS = '_1WJLw'


class SCLS:  # css classes used within search offers
    OFFERS = '_3aiCi'
    MAIN_ANKER = '_16dGT'
    LOCATION = '_3f6Er'
    DATE = '_1kvIw'
    LINK = '_16dGT'
    DESCRIPTION = '_2c4Jo'
    PRICE = '_6HJe5'


class POS:
    ADJ = 'ADJ'  # adjective, e.g. 'warmes' (Innenfutter)
    ADP = 'ADP'  # AD, e.g. 'in', 'Dank'
    ADV = 'ADV'  # adverb, e.g. 'kaum' (gebraucht)
    NUM = 'NUM'  # number, e.g. 37
    NOUN = 'NOUN'  # noun, e.g. 'Goretex'
    PART = 'PART'  # partical, e.g. 'zu' (verkaufen)
    PROPN = 'PROPN'  # proper noun, e.g. 'Wanderschuhe'
    PUNCT = 'PUNCT'  # punctuation, e.g. ','
    VERB = 'VERB'  # verb, e.g. 'verkaufen'

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



