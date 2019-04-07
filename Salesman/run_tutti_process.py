"""
Description: This module is the manually starting point our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.myprofiler import MyProfiler
from tutti import Tutti
from time import sleep

tutti = Tutti(with_browser=True, with_nlp=True, write_to_excel=False, load_sm=True)
# tutti.check_my_offers_against_similar_offers()
# tutti.check_my_virtual_offers_against_similar_offers()
# tutti.check_my_nth_offer_against_similar_offers(1)
tutti.check_my_nth_virtual_offer_against_similar_offers(1)
sleep(2)
