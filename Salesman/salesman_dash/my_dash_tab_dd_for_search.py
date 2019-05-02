"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from sertl_analytics.mydash.my_dash_components import DropDownHandler
from sertl_analytics.constants.salesman_constants import SLSRC, PRCAT
from salesman_tutti.tutti_categorizer import RegionCategorizer, ProductCategorizer


class SRDD:  # Search drop down
    SEARCH_SOURCE = 'SEARCH_SOURCE'
    SEARCH_REGION = 'SEARCH_REGION'
    PRODUCT_CATEGORY = 'PRODUCT_CATEGORY'
    PRODUCT_SUB_CATEGORY = 'PRODUCT_SUB_CATEGORY'

    @staticmethod
    def get_all_as_list():
        return [SRDD.SEARCH_SOURCE, SRDD.SEARCH_REGION, SRDD.PRODUCT_CATEGORY, SRDD.PRODUCT_SUB_CATEGORY]


class SearchTabDropDownHandler(DropDownHandler):
    def __init__(self):
        self._region_categorizer = RegionCategorizer()
        self._product_categorizer = ProductCategorizer()
        DropDownHandler.__init__(self)
        self.selected_search_source = ''
        self.selected_search_region = ''
        self.selected_product_category = ''
        self.selected_product_sub_category = ''

    @property
    def my_search_source_dd(self):
        return 'my_search_source'

    @property
    def my_search_region_dd(self):
        return 'my_search_region'

    @property
    def my_product_category_dd(self):
        return 'my_search_product_category'

    @property
    def my_product_sub_category_dd(self):
        return 'my_search_product_sub_category'

    def __get_drop_down_key_list__(self):
        return SRDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {SRDD.SEARCH_SOURCE: '', SRDD.SEARCH_REGION: '',
                SRDD.PRODUCT_CATEGORY: '', SRDD.PRODUCT_SUB_CATEGORY: ''}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            SRDD.SEARCH_SOURCE: 'Search source',
            SRDD.SEARCH_REGION: 'Region',
            SRDD.PRODUCT_CATEGORY: 'Category',
            SRDD.PRODUCT_SUB_CATEGORY: 'Subcategory',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            SRDD.SEARCH_SOURCE: self.my_search_source_dd,
            SRDD.SEARCH_REGION: self.my_search_region_dd,
            SRDD.PRODUCT_CATEGORY: self.my_product_category_dd,
            SRDD.PRODUCT_SUB_CATEGORY: self.my_product_sub_category_dd,
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            SRDD.SEARCH_SOURCE: default_value if default_value else SLSRC.TUTTI_CH,
            SRDD.SEARCH_REGION: default_value if default_value else '',
            SRDD.PRODUCT_CATEGORY: default_value if default_value else '',
            SRDD.PRODUCT_SUB_CATEGORY: default_value if default_value else '',
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            SRDD.SEARCH_SOURCE: 170,
            SRDD.SEARCH_REGION: 200,
            SRDD.PRODUCT_CATEGORY: 200,
            SRDD.PRODUCT_SUB_CATEGORY: 200,
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            SRDD.SEARCH_SOURCE: self.__get_search_source_options__(),
            SRDD.SEARCH_REGION: self.__get_search_region_options__(),
            SRDD.PRODUCT_CATEGORY: self.__get_product_category_options__(),
            SRDD.PRODUCT_SUB_CATEGORY: self.__get_product_sub_category_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type in [SRDD.SEARCH_SOURCE]:
            return False
        return False

    @staticmethod
    def __get_search_source_options__():
        return [{'label': value, 'value': value} for value in SLSRC.get_search_sources()]

    def __get_search_region_options__(self):
        category_value_list = self._region_categorizer.get_category_value_list()
        return [{'label': value_list[0], 'value': value_list[1]} for value_list in category_value_list]

    def __get_product_category_options__(self):
        category_value_list = self._product_categorizer.get_category_value_list()
        return [{'label': value_list[0], 'value': value_list[1]} for value_list in category_value_list]

    def __get_product_sub_category_options__(self, category=PRCAT.VEHICELS):
        sub_category_list = self._product_categorizer.get_sub_category_lists_for_category(category=category)
        print('{}: sub_category_list={}'.format(category, sub_category_list))
        return [{'label': value_list[0], 'value': value_list[1]} for value_list in sub_category_list]
