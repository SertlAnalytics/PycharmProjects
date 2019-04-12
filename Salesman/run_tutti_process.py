"""
Description: This module is the manually starting point our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.myprofiler import MyProfiler
from tutti import Tutti
from time import sleep
from salesman_system_configuration import SystemConfiguration

sys_config = SystemConfiguration()
sys_config.with_browser = False
sys_config.with_nlp = True
sys_config.write_to_excel = False
sys_config.load_sm = True
sys_config.write_offers_to_database = False

tutti = Tutti(sys_config)
# tutti.check_my_offers_against_similar_offers()
# tutti.check_my_virtual_offers_against_similar_offers()
# tutti.check_my_nth_offer_against_similar_offers(1)
tutti.check_my_nth_virtual_offer_against_similar_offers(1)
sleep(2)
