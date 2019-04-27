"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from sertl_analytics.mydash.my_dash_components import DropDownHandler
from sertl_analytics.constants.salesman_constants import SLSRC


class PRDD:  # Pricing drop down
    SIMILAR_SALE_SOURCE = 'SIMILAR_SALE_SOURCE'

    @staticmethod
    def get_all_as_list():
        return [PRDD.SIMILAR_SALE_SOURCE]


class PricingTabDropDownHandler(DropDownHandler):
    def __init__(self):
        DropDownHandler.__init__(self)
        self.selected_similar_sale_source = ''

    @property
    def my_pricing_similar_sales_source_dd(self):
        return 'my_pricing_similar_sales_source'

    def __get_drop_down_key_list__(self):
        return PRDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {PRDD.SIMILAR_SALE_SOURCE: ''}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            PRDD.SIMILAR_SALE_SOURCE: 'Similar sale source',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            PRDD.SIMILAR_SALE_SOURCE: self.my_pricing_similar_sales_source_dd,
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            PRDD.SIMILAR_SALE_SOURCE: default_value if default_value else SLSRC.TUTTI_CH,
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            PRDD.SIMILAR_SALE_SOURCE: 200,
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            PRDD.SIMILAR_SALE_SOURCE: self.__get_similar_trade_source_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type in [PRDD.SIMILAR_SALE_SOURCE]:
            return False
        return False

    @staticmethod
    def __get_similar_trade_source_options__():
        return [{'label': value, 'value': value} for value in SLSRC.get_similar_sale_sources()]
