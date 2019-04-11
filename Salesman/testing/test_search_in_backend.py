"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-08
"""

import requests
from lxml import html
from lxml.html import HtmlElement
from tutti_spacy import TuttiSpacy
from tutti_offer import TuttiOffer
from tutti_constants import OCLS
from sertl_analytics.myhtml import MyHtmlElement


class TuttiPage:
    def __init__(self):
        self._url_search_q = 'https://www.tutti.ch/de/li/ganze-schweiz?q='
        self._spacy = TuttiSpacy(load_sm=True)

    def search(self, search_str: str):
        url = '{}{}'.format(self._url_search_q, search_str)
        print('Searching for {}'.format(url))
        request = requests.get(url)
        tree = html.fromstring(request.content)
        offers = tree.xpath('//div[@class="_3aiCi"]')
        for offer_element in offers:
            offer = TuttiOffer(self._spacy.nlp, search_str)
            offer.init_by_html_element(offer_element)
            offer.print_offer_in_original_structure()


tutti_page = TuttiPage()
tutti_page.search('eames alu chair')

