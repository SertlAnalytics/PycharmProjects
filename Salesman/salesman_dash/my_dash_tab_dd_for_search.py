"""
Description: This module contains the drop downs for the tab recommender for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-17
"""

from sertl_analytics.mydash.my_dash_components import DropDownHandler
from sertl_analytics.constants.salesman_constants import SLSRC
from salesman_tutti.tutti_constants import PRCAT
from salesman_system_configuration import SystemConfiguration
from salesman_database.access_layer.access_layer_file import MySalesAccessLayerFile


class SRDD:  # Search drop down
    SEARCH_SOURCE = 'SEARCH_SOURCE'
    SEARCH_REGION = 'SEARCH_REGION'
    SEARCH_CATEGORY = 'SEARCH_CATEGORY'
    SEARCH_SUB_CATEGORY = 'SEARCH_SUB_CATEGORY'
    SEARCH_ENTITIES = 'SEARCH_ENTITIES'
    SEARCH_DATABASE = 'SEARCH_DATABASE'
    SEARCH_FILE = 'SEARCH_FILE'

    @staticmethod
    def get_all_as_list():
        return [SRDD.SEARCH_SOURCE, SRDD.SEARCH_REGION, SRDD.SEARCH_CATEGORY, SRDD.SEARCH_SUB_CATEGORY,
                SRDD.SEARCH_DATABASE, SRDD.SEARCH_FILE]


class SearchTabDropDownHandler(DropDownHandler):
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        DropDownHandler.__init__(self)
        self.selected_search_entities = ''
        self.selected_database_row_id = ''
        self.selected_file_row = ''

    @property
    def my_search_source_dd(self):
        return 'my_search_source'

    @property
    def my_search_region_dd(self):
        return 'my_search_region'

    @property
    def my_search_category_dd(self):
        return 'my_search_category'

    @property
    def my_search_sub_category_dd(self):
        return 'my_search_sub_category'

    @property
    def my_search_entities_dd(self):
        return 'my_search_entities'

    @property
    def my_search_db_dd(self):
        return 'my_search_db_dd'

    @property
    def my_search_file_dd(self):
        return 'my_search_file_dd'

    def __get_drop_down_key_list__(self):
        return SRDD.get_all_as_list()

    def __get_selected_value_dict__(self):
        return {SRDD.SEARCH_SOURCE: '', SRDD.SEARCH_REGION: '',
                SRDD.SEARCH_CATEGORY: '', SRDD.SEARCH_SUB_CATEGORY: '', SRDD.SEARCH_ENTITIES: '',
                SRDD.SEARCH_DATABASE: '', SRDD.SEARCH_FILE: ''}

    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            SRDD.SEARCH_SOURCE: 'Search source',
            SRDD.SEARCH_REGION: 'Region',
            SRDD.SEARCH_CATEGORY: 'Category',
            SRDD.SEARCH_SUB_CATEGORY: 'Subcategory',
            SRDD.SEARCH_ENTITIES: 'Entities',
            SRDD.SEARCH_DATABASE: '',
            SRDD.SEARCH_FILE: '',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            SRDD.SEARCH_SOURCE: self.my_search_source_dd,
            SRDD.SEARCH_REGION: self.my_search_region_dd,
            SRDD.SEARCH_CATEGORY: self.my_search_category_dd,
            SRDD.SEARCH_SUB_CATEGORY: self.my_search_sub_category_dd,
            SRDD.SEARCH_ENTITIES: self.my_search_entities_dd,
            SRDD.SEARCH_DATABASE: self.my_search_db_dd,
            SRDD.SEARCH_FILE: self.my_search_file_dd,

        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None):
        default_dict = {
            SRDD.SEARCH_SOURCE: default_value if default_value else SLSRC.TUTTI_CH,
            SRDD.SEARCH_REGION: default_value if default_value else '',
            SRDD.SEARCH_CATEGORY: default_value if default_value else '',
            SRDD.SEARCH_SUB_CATEGORY: default_value if default_value else '',
            SRDD.SEARCH_ENTITIES: default_value if default_value else '',
            SRDD.SEARCH_DATABASE: default_value if default_value else '',
            SRDD.SEARCH_FILE: default_value if default_value else '',
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            SRDD.SEARCH_SOURCE: 170,
            SRDD.SEARCH_REGION: 200,
            SRDD.SEARCH_CATEGORY: 200,
            SRDD.SEARCH_SUB_CATEGORY: 200,
            SRDD.SEARCH_ENTITIES: 350,
            SRDD.SEARCH_DATABASE: 650,
            SRDD.SEARCH_FILE: 650,
        }
        return value_dict.get(drop_down_type, 140)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            SRDD.SEARCH_SOURCE: self.__get_search_source_options__(),
            SRDD.SEARCH_REGION: self.__get_search_region_options__(),
            SRDD.SEARCH_CATEGORY: self.__get_product_category_options__(),
            SRDD.SEARCH_SUB_CATEGORY: self.__get_product_sub_category_options__(),
            SRDD.SEARCH_ENTITIES: self.__get_product_print_category_options__(),
            SRDD.SEARCH_DATABASE: self.__get_database_options__(),
            SRDD.SEARCH_FILE: self.__get_file_options__(),
        }

    def __get_for_multi__(self, drop_down_type: str):
        if drop_down_type in [SRDD.SEARCH_ENTITIES]:
            return True
        return False

    @staticmethod
    def __get_search_source_options__():
        return [{'label': value, 'value': value} for value in SLSRC.get_search_sources()]

    def __get_search_region_options__(self):
        return self.sys_config.region_categorizer.get_category_value_list_as_option_list()

    def __get_product_category_options__(self):
        return self.sys_config.product_categorizer.get_category_value_list_as_option_list()

    def __get_product_sub_category_options__(self, category=PRCAT.VEHICELS):
        return self.sys_config.product_categorizer.get_sub_category_lists_for_category_as_option_list(category=category)

    @staticmethod
    def __get_product_print_category_options__():
        return [{'label': '', 'value': ''}]

    def __get_database_options__(self):
        return self.sys_config.access_layer_sale.get_my_sales_as_dd_options()

    def __get_file_options__(self):
        return self.sys_config.access_layer_file.get_my_sales_as_dd_options()

