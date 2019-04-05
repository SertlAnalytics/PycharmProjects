"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from tutti_browser import MyUrlBrowser4Tutti
from tutti_offer import TuttiOffer
from spacy import displacy
from tutti_spacy import TuttiSpacy


class Tutti:
    def __init__(self):
        self._spacy = TuttiSpacy()
        self._my_offers = None
        self._similar_offer_dict = {}  # key is the ID of my_offer
        self._browser = MyUrlBrowser4Tutti(self._spacy.nlp)
        self._browser.enter_and_submit_credentials()

    @property
    def nlp(self):
        return self._spacy.nlp

    def check_my_nth_offer(self, number=1):
        offer = self._browser.get_my_nth_offer_from_tutti(number)
        if offer is None:
            return
        offer.print_offer_in_original_structure()

    def check_my_offers_against_similar_offers(self):
        self._my_offers = self._browser.get_my_offers_from_tutti()
        self._similar_offer_dict = self._browser.get_similar_offer_dict_from_tutti(self._my_offers)


    def __visualize_dependencies__(self):
        for offer in self._my_offers:
            doc_dict = {'Title': self.nlp(offer.title), 'Description': self.nlp(offer.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

