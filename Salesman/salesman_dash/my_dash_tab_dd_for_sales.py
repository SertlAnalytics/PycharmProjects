"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from sertl_analytics.mydash.my_dash_components import DropDownHandler
from sertl_analytics.constants.salesman_constants import SLSRC, PRCAT
from salesman_tutti.tutti_categorizer import RegionCategorizer, ProductCategorizer
from salesman_system_configuration import SystemConfiguration


class SLDD:  # SALE drop down
    SALE_SOURCE = 'SALE_SOURCE'
    SALE_REGION = 'SALE_REGION'
    SALE_CATEGORY = 'SALE_CATEGORY'
    SALE_SUB_CATEGORY = 'SALE_SUB_CATEGORY'

    @staticmethod
    def get_all_as_list():
        return [SLDD.SALE_SOURCE, SLDD.SALE_REGION, SLDD.SALE_CATEGORY, SLDD.SALE_SUB_CATEGORY]


class SaleTabDropDownHandler(DropDownHandler):
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        DropDownHandler.__init__(self)
        self.selected_sale_source = ''
        self.selected_sale_region = ''
        self.selected_sale_category = ''
        self.selected_sale_sub_category = ''

    @property
    def my_sale_source_dd(self):
        return 'my_sale_source'

    @property
    def my_sale_region_dd(self):
        return 'my_sale_region'

    @property
    def my_sale_category_dd(self):
        return 'my_sale_category'

    @property
    def my_sale_sub_category_dd(self):
        return 'my_sale_sub_category'

    def __get_drop_down_key_list__(self):
        return SLDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {SLDD.SALE_SOURCE: '', SLDD.SALE_REGION: '',
                SLDD.SALE_CATEGORY: '', SLDD.SALE_SUB_CATEGORY: ''}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            SLDD.SALE_SOURCE: 'Sale source',
            SLDD.SALE_REGION: 'Region',
            SLDD.SALE_CATEGORY: 'Category',
            SLDD.SALE_SUB_CATEGORY: 'Subcategory',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            SLDD.SALE_SOURCE: self.my_sale_source_dd,
            SLDD.SALE_REGION: self.my_sale_region_dd,
            SLDD.SALE_CATEGORY: self.my_sale_category_dd,
            SLDD.SALE_SUB_CATEGORY: self.my_sale_sub_category_dd,
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            SLDD.SALE_SOURCE: default_value if default_value else SLSRC.DB,
            SLDD.SALE_REGION: default_value if default_value else '',
            SLDD.SALE_CATEGORY: default_value if default_value else '',
            SLDD.SALE_SUB_CATEGORY: default_value if default_value else '',
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            SLDD.SALE_SOURCE: 170,
            SLDD.SALE_REGION: 200,
            SLDD.SALE_CATEGORY: 200,
            SLDD.SALE_SUB_CATEGORY: 200,
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            SLDD.SALE_SOURCE: self.__get_sale_source_options__(),
            SLDD.SALE_REGION: self.__get_sale_region_options__(),
            SLDD.SALE_CATEGORY: self.__get_product_category_options__(),
            SLDD.SALE_SUB_CATEGORY: self.__get_product_sub_category_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type in [SLDD.SALE_SOURCE]:
            return False
        return False

    @staticmethod
    def __get_sale_source_options__():
        return [{'label': value, 'value': value} for value in SLSRC.get_sale_sources()]

    def __get_sale_region_options__(self):
        category_value_list = self.sys_config.region_categorizer.get_category_value_list()
        return [{'label': value_list[0], 'value': value_list[1]} for value_list in category_value_list]

    def __get_product_category_options__(self):
        return self.sys_config.product_categorizer.get_category_value_list_as_option_list()

    def __get_product_sub_category_options__(self, category=PRCAT.VEHICELS):
        return self.sys_config.product_categorizer.get_sub_category_lists_for_category_as_option_list(category=category)

