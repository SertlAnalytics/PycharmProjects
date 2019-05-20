"""
Description: This module contains the factory class for sale entity
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, SLST
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_url_factory import SalesmanSearchApi
from salesman_sale import SalesmanSale
from salesman_web_parser import SalesmanWebParser
from salesman_sale_checks import SaleIdenticalCheck, SaleSimilarityCheck


class SalesmanSaleFactory:
    def __init__(self, sys_config: SystemConfiguration, salesman_spacy: SalesmanSpacy):
        self.sys_config = sys_config
        self._access_layer_sale = self.sys_config.access_layer_sale
        self._salesman_spacy = salesman_spacy
        self._web_parser = SalesmanWebParser(self.sys_config, self._salesman_spacy)
        self._online_search_api = None

    @property
    def sale_factory_source(self) -> str:
        return SLSRC.TUTTI_CH

    def are_sales_similar_on_platform_by_sale_id(self, sale_id_01: str, sale_id_02: str) -> bool:
        sale_01 = self.get_sale_via_request_by_sale_id(sale_id_01)
        sale_02 = self.get_sale_via_request_by_sale_id(sale_id_02)
        if sale_01 is None or sale_02 is None:
            return False
        return self.are_sales_similar(sale_01, sale_02, True)

    def are_sales_similar_in_db_by_sale_id(self, sale_id_01: str, sale_id_02: str) -> bool:
        sale_01 = self.get_sale_from_db_by_sale_id(sale_id_01)
        sale_02 = self.get_sale_from_db_by_sale_id(sale_id_02)
        if sale_01 is None or sale_02 is None:
            return False
        return self.are_sales_similar(sale_01, sale_02, True)

    def write_sales_after_checks_to_db(self, sales: list, sale_master: SalesmanSale=None, enforce_writing=False):
        if not(self.sys_config.write_to_database or enforce_writing):
            return

        self._access_layer_sale.reset_counters()
        if sale_master is not None:
            self.write_sale_after_checks_to_db(sale_master, enforce_writing=enforce_writing)
        for sale in sales:
            self.write_sale_after_checks_to_db(sale, sale_master, enforce_writing)
        print('Sale transactions: insert={}, updates={}'.format(
            self._access_layer_sale.counter_insert, self._access_layer_sale.counter_update))

    def write_sale_after_checks_to_db(self, sale: SalesmanSale, sale_master: SalesmanSale=None, enforce_writing=False):
        if not(self.sys_config.write_to_database or enforce_writing):
            return
        if not sale.is_sale_ready_for_sale_table():
            return

        sale_dict = sale.get_data_dict_for_sale_table()
        sale_from_db = self.get_sale_from_db_by_sale_id(sale.sale_id)
        master_id = '' if sale_master is None else sale_master.sale_id
        if sale_from_db is None:
            self._access_layer_sale.insert_sale_data([sale_dict])
        else:
            today_str = MyDate.get_date_str_from_datetime()

            if sale_from_db.last_check_date == today_str:
                return
            identical_check = SaleIdenticalCheck(sale, sale_from_db, number_from_db=2)

            if identical_check.are_identical:
                if sale_from_db.last_check_date != today_str:
                    self.update_last_check_date(sale_from_db, today_str)
            else:
                sale_dict[SLDC.COMMENT] = 'Changes: {}'.format(identical_check.different_columns)
                sale_dict[SLDC.START_DATE] = today_str  # we change the start date since some changes....
                self._access_layer_sale.insert_sale_data([sale_dict])
        if master_id != '':
            self._access_layer_sale.insert_or_update_sale_relation_data(
                sale_from_db.get_data_dict_for_sale_relation_table(master_id))

    @staticmethod
    def are_sales_similar(source_sale: SalesmanSale, other_sale: SalesmanSale, with_info=True) -> bool:
        check = SaleSimilarityCheck(source_sale, other_sale)
        if with_info and not check.are_sales_similar:
            print('Not similar because of {}:'.format(check.similar_label))
            print('...{}: {}'.format(source_sale.sale_id, source_sale.get_value(SLDC.ENTITY_LABELS_DICT)))
            print('...{}: {}'.format(other_sale.sale_id, other_sale.get_value(SLDC.ENTITY_LABELS_DICT)))
        return check.are_sales_similar

    def get_sales_from_db_by_sale_state(self, sale_state: str, only_own_sales=False) -> list:
        df = self._access_layer_sale.get_sales_df_by_sale_state(sale_state, only_own_sales)
        # MyPandas.print_df_details(df)
        sales = []
        for idx, row in df.iterrows():
            sales.append(self.get_sale_by_db_row(row))
        return sales

    def get_similar_sales_for_master_sale_from_db(self, master_sale: SalesmanSale):
        df = self._access_layer_sale.get_sales_df_by_master_sale_id(master_sale.sale_id)
        # MyPandas.print_df_details(df)
        sales = []
        for idx, row in df.iterrows():
            sales.append(self.get_sale_by_db_row(row))
        return sales

    def check_status_of_sales_in_database(self):
        today_str = MyDate.get_date_str_from_datetime()
        sale_ids = self._access_layer_sale.get_sale_ids_from_db_by_sale_state(SLST.OPEN)
        for idx, sale_id in enumerate(sale_ids):
            sale_available = self.can_sale_be_accessed_via_request_by_sale_id(sale_id)
            print('{}/{}: Check_status_of_sales_in_database: {} - Result: {}'.format(
                idx + 1, len(sale_ids), sale_id, sale_available))
            if not sale_available:
                self._access_layer_sale.change_sale_state(sale_id, SLST.VANISHED, today_str)

    def check_similarity_against_master_sale(
            self, source_sale: SalesmanSale, similar_sales_in_db: list, change_in_db=False):
        row_id_list = []
        for similar_sale_in_db in similar_sales_in_db:
            if self.are_sales_similar(source_sale, similar_sale_in_db, True):
                pass
            else:
                similar_sale_in_db.set_value(SLDC.SALE_STATE, SLST.DELETE)
                row_id_list.append(str(similar_sale_in_db.row_id))
        print('row_id_list to set to delete: {}'.format(row_id_list))
        if change_in_db and len(row_id_list) > 0:
            last_check_date = MyDate.get_date_str_from_datetime()
            changed = self._access_layer_sale.change_sale_state_for_rowid_list(SLST.DELETE, row_id_list, last_check_date)
            print('Changed in db: {}'.format(changed))

    def adjust_web_parser_by_search_api(self, api: SalesmanSearchApi):
        self._web_parser.adjust_by_search_api(api)

    def get_search_string_found_number_dict(self, search_label_lists: list) -> dict:
        return self._web_parser.get_search_string_found_number_dict(search_label_lists)

    def get_sale_from_db_by_sale_id(self, sale_id: str) -> SalesmanSale:
        if self.sys_config.access_layer_sale.is_sale_with_id_available(sale_id):
            df = self.sys_config.access_layer_sale.get_sale_by_id(sale_id)
            return self.get_sale_by_db_row(df.iloc[0])

    def get_sale_from_db_by_row_id(self, row_id: int) -> SalesmanSale:
        df = self.sys_config.access_layer_sale.get_sale_by_row_id(row_id)
        return self.get_sale_by_db_row(df.iloc[0])

    def get_sale_from_file_by_row_number(self, row_number: int) -> SalesmanSale:
        row = self.sys_config.access_layer_file.get_row(row_number)
        return self.get_sale_by_file_row(row)

    def fill_search_api_list_by_found_numbers(self, api_list: list, search_label_lists: list):
        self._web_parser.fill_search_api_list_by_found_numbers(api_list, search_label_lists)

    def get_sale_by_search_api(self, api: SalesmanSearchApi) -> SalesmanSale:
        sale_data_dict = self.__get_sales_data_dict_for_online_search_api__(api)
        return self.__get_sale_by_data_dict__(sale_data_dict)

    def get_sale_via_request_by_sale_id(self, sale_id: str) -> SalesmanSale:
        sale_data_dict = self._web_parser.get_sale_data_dict_for_sale_id(sale_id)
        # print('sale_data_dict={}'.format(sale_data_dict))
        if len(sale_data_dict) == 0:
            print('\nWARNING: No active sale found on {} for id={}'.format(self.sale_factory_source, sale_id))
        else:
            return self.__get_sale_by_data_dict__(sale_data_dict)

    def can_sale_be_accessed_via_request_by_sale_id(self, sale_id: str) -> bool:
        sale_data_dict = self._web_parser.get_sale_data_dict_for_sale_id(sale_id)
        return len(sale_data_dict) > 0

    def get_sales_by_search_label_list(self, search_label_list: list) -> list:
        return_sales = []
        sales_data_dict = self._web_parser.get_sales_data_dict_for_search_label_list(search_label_list)
        for sale_id, sale_data_dict in sales_data_dict.items():
            sale = self.__get_sale_by_data_dict__(sale_data_dict, ', '.join(search_label_list))
            return_sales.append(sale)
        return return_sales

    def get_sale_by_browser_sale_element(self, sale_element, search_labels):
        sale_data_dict = self._web_parser.get_sale_data_dict_by_browser_sale_element(sale_element)
        sale_data_dict[SLDC.IS_MY_SALE] = True
        return self.__get_sale_by_data_dict__(sale_data_dict, search_labels)

    def get_sale_by_file_row(self, row):
        sale_data_dict = {col: row[col] for col in row.index}
        sale_data_dict[SLDC.IS_MY_SALE] = True
        sale_data_dict[SLDC.LOCATION] = 'virtual'
        sale_data_dict[SLDC.START_DATE] = MyDate.get_date_as_string_from_date_time()
        return self.__get_sale_by_data_dict__(sale_data_dict)

    def get_sale_by_db_row(self, row):
        sale_data_dict = {col: row[col] for col in row.index}
        return self.__get_sale_by_data_dict__(sale_data_dict, is_from_db=True)

    def update_last_check_date(self, sale: SalesmanSale, date_new: str):
        self._access_layer_sale.update_sale_last_check_date(sale.sale_id, sale.version, date_new)

    def __get_sales_data_dict_for_online_search_api__(self, api):
        region = self.sys_config.region_categorizer.get_category_for_value(api.region_value)
        # print('__get_sales_data_dict_for_online_search_api__: region={}'.format(region))
        product_category, product_sub_category = '', ''
        if api.category_value != '':
            product_category = self.sys_config.product_categorizer.get_category_for_value(api.category_value)
            product_sub_category = self.sys_config.product_categorizer.get_sub_category_for_value(
                product_category, api.sub_category_value)
        sale_data_dict = {
            SLDC.SALE_ID: str(MyDate.time_stamp_now()),
            SLDC.LOCATION: 'online',
            SLDC.START_DATE: MyDate.get_date_as_string_from_date_time(),
            SLDC.TITLE: api.search_string,
            SLDC.REGION: region,
            SLDC.PRODUCT_CATEGORY: product_category,
            SLDC.PRODUCT_SUB_CATEGORY: product_sub_category,
        }
        # print('sale_data_dict={}'.format(sale_data_dict))
        return sale_data_dict

    def __get_sale_by_data_dict__(self, sale_data_dict: dict, search_labels='', is_from_db=False):
        is_my_offer = sale_data_dict.get(SLDC.IS_MY_SALE, False)
        sale = self.__get_sale_initialized__(sale_data_dict[SLDC.SALE_ID], search_labels, is_my_offer=is_my_offer)
        sale.add_value_dict(sale_data_dict)
        sale.complete_sale(is_from_db)
        return sale

    def __get_sale_initialized__(self, sale_id: str, found_by_labels='', is_my_offer=False):
        sale = SalesmanSale(self._salesman_spacy, self.sys_config, found_by_labels=found_by_labels, is_my_sale=is_my_offer)
        sale.set_value(SLDC.SOURCE, self.sale_factory_source)
        sale.set_value(SLDC.SALE_ID, sale_id)
        return sale



