"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.constants.salesman_constants import SLDC, SLSRC, SLST
from sertl_analytics.processes.my_process import MyProcessCounter
from sertl_analytics.my_excel import MyExcel
from sertl_analytics.mydates import MyDate
from calculation.outlier import Outlier
from salesman_tutti.tutti_browser import MyUrlBrowser4Tutti
from salesman_sale import SalesmanSale
from spacy import displacy
from salesman_nlp.salesman_spacy import SalesmanSpacy
import pandas as pd
from salesman_system_configuration import SystemConfiguration
from printing.sale_printing import SalesmanPrint
from salesman_tutti.tutti_url_factory import SalesmanSearchApi
from factories.salesman_sale_factory import SalesmanSaleFactory
from factories.salesman_entity_factory import SalesmanEntityFactory
from salesman_sale_checks import SaleIdenticalCheck, SaleSimilarityCheck
from salesman_search_data import SalesmanSearchData
from time import sleep


class Tutti:
    def __init__(self, sys_config: SystemConfiguration):
        self.sys_config = sys_config
        self._printing = None
        self._sale_platform = self.__get_sale_platform__()
        self._excel = self.__get_excel__()
        if self.sys_config.with_nlp:
            self._salesman_spacy = SalesmanSpacy(
                entity_handler=sys_config.entity_handler, load_sm=self.sys_config.load_sm)
        else:
            self._salesman_spacy = None
        self._sale_factory = SalesmanSaleFactory(self.sys_config, self._salesman_spacy)
        self._entity_factory = SalesmanEntityFactory(self.sys_config)
        self._browser = None
        self._current_source_sale = None
        self._current_similar_sales = []  # will get the results for the search for ONE source

    @property
    def platform_name(self) -> str:
        return SLSRC.TUTTI_CH

    @property
    def salesman_spacy(self):
        return self._salesman_spacy

    @property
    def nlp(self):
        return None if self._salesman_spacy is None else self._salesman_spacy.nlp

    @property
    def printing(self) -> SalesmanPrint:
        return self._printing

    @property
    def current_source_sale(self) -> SalesmanSale:
        return self._current_source_sale

    @property
    def browser(self) -> MyUrlBrowser4Tutti:
        if self._browser is None:
            self._browser = MyUrlBrowser4Tutti(self.sys_config, self._salesman_spacy, self._sale_factory)
            self._browser.enter_and_submit_credentials()
            sleep(2)
        return self._browser

    @property
    def excel_file_path(self) -> str:
        return self.sys_config.file_handler.get_file_path_for_file(
            '{}_{}'.format(self._sale_platform, self.sys_config.sales_result_file_name))

    def close_excel(self):
        if self.sys_config.write_to_excel:
            self._excel.close()

    def get_entity_based_search_lists(self):
        return self._current_source_sale.get_entity_based_search_lists()

    def get_sale_from_db_by_sale_id(self, sale_id: str):
        sale = self._sale_factory.get_sale_from_db_by_sale_id(sale_id)
        data_dict = sale.get_data_dict_for_sale_table()
        print('data_dict={}'.format(data_dict))
        return sale

    def check_search_by_api_against_similar_sales(self, api: SalesmanSearchApi):
        sale = self._sale_factory.get_sale_by_search_api(api)
        self.__check_sales_against_similar_sales_on_platform__([sale])

    def check_search_by_api_against_other_sale(self, api: SalesmanSearchApi, other_sale_id: str):
        self._current_source_sale = self._sale_factory.get_sale_by_search_api(api)
        sale_other = self.get_sale_from_platform_by_sale_id(other_sale_id)
        if sale_other is None:
            print('Sale "{}" not found on Tutti'.format(other_sale_id))
        else:
            sale_similarity_check = SaleSimilarityCheck(self._current_source_sale, sale_other)
            if sale_similarity_check.are_sales_similar:
                print('Both are similar')
            else:
                print('Sales are NOT similar - label: {}'.format(sale_similarity_check.similar_label))
            self._current_similar_sales = [sale_other]
            self.__process_my_sale_and_similar_sales__()

    def check_my_nth_sale_in_browser_against_similar_sales(self, number=1):
        sale = self.browser.get_my_nth_sale_from_tutti(number)
        self.__check_sales_against_similar_sales_on_platform__([sale])

    def check_my_nth_sale_in_browser_against_database(self, number=1):
        sale = self.browser.get_my_nth_sale_from_tutti(number)
        if sale is None:
            print('Sale on position "{}" not found on {}'.format(number, self.platform_name))
        else:
            sale.print_sale_details()
            self.__write_sale_to_database__(sale)

    def check_status_of_sales_in_database(self, process_counter: MyProcessCounter):
        self._sale_factory.check_status_of_sales_in_database(process_counter)

    def check_own_sales_in_database_against_similar_sales(self, process_counter: MyProcessCounter):
        sales = self._sale_factory.get_sales_from_db_by_sale_state(SLST.OPEN, only_own_sales=True)
        process_counter.processed_records = len(sales)
        for idx, sale in enumerate(sales):
            print('{}/{}: check_own_in_database_against_similar_sales: {}'.format(idx + 1, len(sales), sale.sale_id))
            self.__check_sales_against_similar_sales_on_platform__([sale])

    def check_my_sales_in_browser_against_database(self, state='active'):
        state_list = ['active', 'pending', 'edit', 'hidden', 'archived'] if state == '' else [state]
        for state in state_list:
            source_sale_list = self.browser.get_my_sales_from_tutti()
            for source_sale in source_sale_list:
                source_sale.print_sale_details()
                self.__write_sale_to_database__(source_sale)

    def check_sale_on_platform_against_similar_sales_by_sale_id(self, sale_id: str):
        sale = self.get_sale_from_platform_by_sale_id(sale_id)
        self.__check_sales_against_similar_sales_on_platform__([sale])

    def inspect_sales_on_platform_for_api(self, api: SalesmanSearchApi):
        sales = self.__get_sales_on_platform_for_api__(api)
        self.__write_to_excel__(sales)
        entity_dict_summary = {}
        for sale in sales:
            for value, label in sale.entity_label_values_dict.items():
                entity_dict_summary[value] = label
        print('entity_dict_summary={}'.format(entity_dict_summary))

    def check_sale_in_db_against_similar_sales_on_platform_by_sale_id(self, sale_id: str):
        sale = self._sale_factory.get_sale_from_db_by_sale_id(sale_id)
        if sale is None:
            print('\nWARNING: No sale in database with ID={}'.format(sale_id))
        else:
            self.__check_sales_against_similar_sales_on_platform__([sale])

    def check_similar_sales_in_db_against_master_sale_in_db(self, process_counter: MyProcessCounter, master_sale_id=''):
        self._sale_factory.reset_access_layer_counters()
        if master_sale_id == '':
            master_sales = self._sale_factory.get_sales_from_db_by_sale_state(SLST.OPEN, only_own_sales=True)
        else:
            master_sale = self._sale_factory.get_sale_from_db_by_sale_id(master_sale_id)
            if master_sale is None:
                print('\nWARNING: No sale in database with ID={}'.format(master_sale_id))
                return
            else:
                master_sales = [master_sale]
        self.__check_similar_sales_in_db_against_master_sales_in_db__(master_sales)
        self._sale_factory.synchronize_process_counter(process_counter)

    def check_sales_for_similarity_by_sale_id(self, sale_01_id: str, sale_02_id: str):
        if self._sale_factory.are_sales_similar_on_platform_by_sale_id(sale_01_id, sale_02_id):
            print('-> Similar on platform')
        if self._sale_factory.are_sales_similar_in_db_by_sale_id(sale_01_id, sale_02_id):
            print('-> Similar in db')

    def check_my_nth_virtual_sale_against_similar_sales(self, number=1):
        source_sale_list = self.__get_my_virtual_sales__(number)
        self.__check_sales_against_similar_sales_on_platform__(source_sale_list)

    def __check_sales_against_similar_sales_on_platform__(self, source_sale_list: list, compare_sale_id=str):
        if len(source_sale_list) == 0 or source_sale_list[0] is None:
            return
        for source_sale in source_sale_list:
            self.__check_sale_against_similar_sales_on_platform__(source_sale)

    def __check_similar_sales_in_db_against_master_sales_in_db__(self, master_sale_list: list):
        if len(master_sale_list) == 0 or master_sale_list[0] is None:
            return
        for master_sale in master_sale_list:
            print('\nCheck similar sales in db against master sale: {}_{}_{}'.format(
                master_sale.sale_id, master_sale.sale_state, master_sale.title))
            self.__check_similar_sales_in_db_against_master_sale_in_db__(master_sale)

    def __check_sale_against_similar_sales_on_platform__(self, sale: SalesmanSale):
        if self.sys_config.print_details:
            sale.print_sale_in_original_structure()
        self._current_source_sale = sale
        sale.print_data_dict()
        self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
        self.__process_my_sale_and_similar_sales__()

    def __check_similar_sales_in_db_against_master_sale_in_db__(self, master_sale: SalesmanSale):
        if self.sys_config.print_details:
            master_sale.print_sale_in_original_structure()
        self._current_source_sale = master_sale
        self._current_similar_sales = self._sale_factory.get_similar_sales_for_master_sale_from_db(
            self._current_source_sale)
        self.__correct_similar_sales_in_db__()

    def print_details_for_sale_on_platform_by_sale_id(self, sale_id: str, with_data_dict=False):
        self.sys_config.write_to_excel = False
        sale = self.get_sale_from_platform_by_sale_id(sale_id)
        if sale is None:
            print('Cannot find {}'.format(sale_id))
        else:
            sale.print_sale_details()
            sale.print_sale_in_original_structure()
            if with_data_dict:
                sale.print_data_dict()

    def check_sale_on_platform_against_sale_in_db_by_sale_id(self, sale_id: str, write_to_db=False):
        sale = self.get_sale_from_platform_by_sale_id(sale_id)
        if sale is None:
            print('Sale "{}" not found on Tutti'.format(sale_id))
        else:
            sale.print_sale_details()
            sale_from_db = self._sale_factory.get_sale_from_db_by_sale_id(sale_id)
            sale_from_db.print_sale_details()
            identical_check = SaleIdenticalCheck(sale, sale_from_db, number_from_db=2)
            print('\nResult: {}'.format('identical' if identical_check.are_identical else 'not identical'))
            if not identical_check.are_identical and write_to_db:
                sale.set_value(SLDC.COMMENT, 'Changes: {}'.format(identical_check.different_columns))
                self.__write_sale_to_database__(sale)

    def get_sale_from_platform_by_sale_id(self, sale_id: str) -> SalesmanSale:
        return self._sale_factory.get_sale_via_request_by_sale_id(sale_id)

    def get_search_results_by_selected_entities(self, selected_entities: list):
        if self._printing is None:
            return []
        self._printing.init_for_selected_plot_categories(selected_entities)
        return self.__get_similar_sales_as_dict_list_by_selected_entities__(selected_entities)

    def __get_similar_sales_as_dict_list_by_selected_entities__(self, selected_entities: list) -> list:
        return_list = []
        if len(selected_entities) == 0:
            for similar_sale in self._current_similar_sales:
                return_list.append(similar_sale.get_data_dict_for_columns(SLDC.get_columns_for_search_results()))
            return return_list
        for similar_sale in self._current_similar_sales:
            has_all_entities = True
            for selected_entity in selected_entities:
                entity_split = selected_entity.split('_')
                if not similar_sale.has_sale_entity(entity_split[1], entity_split[0]):
                    has_all_entities = False
                    break
            if has_all_entities:
                return_list.append(similar_sale.get_data_dict_for_columns(SLDC.get_columns_for_search_results()))
        return return_list

    def get_search_results_by_search_api(self, api: SalesmanSearchApi) -> list:
        if api.search_string == '':
            return []
        self._current_source_sale = self._sale_factory.get_sale_by_search_api(api)
        # self._current_source_sale.print_data_dict()
        self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
        self._printing = SalesmanPrint(self._current_source_sale, self._current_similar_sales)
        return self.__get_similar_sales_as_dict_list__(self._current_similar_sales, for_db=False)

    def check_my_sales_in_browser_against_similar_sales(self, state='active'):
        state_list = ['active', 'pending', 'edit', 'hidden', 'archived'] if state == '' else [state]
        for state in state_list:
            source_sale_list = self.browser.get_my_sales_from_tutti()
            for source_sale in source_sale_list:
                self._current_source_sale = source_sale
                self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
                self.__process_my_sale_and_similar_sales__()

    def check_my_virtual_sales_against_similar_sales(self):
        source_sale_list = self.__get_my_virtual_sales__()
        for source_sale in source_sale_list:
            self._current_source_sale = source_sale
            self._current_similar_sales = self.__get_similar_sales_for_sale__(self._current_source_sale)
            self.__process_my_sale_and_similar_sales__()

    def __process_my_sale_and_similar_sales__(self):
        self.__check_spacy_doc_similarity__(self._current_similar_sales)
        self.__write_to_excel__(self._current_similar_sales)
        self.__write_to_database__(self._current_similar_sales)
        if self.sys_config.plot_results:
            self._printing = SalesmanPrint(self._current_source_sale, self._current_similar_sales)
            self._printing.print_box_plots()

    def __correct_similar_sales_in_db__(self):
        self._sale_factory.check_similarity_against_master_sale(
            self.current_source_sale, self._current_similar_sales, change_in_db=True)
        self.__write_to_excel__(self._current_similar_sales)
        if self.sys_config.plot_results:
            self._printing = SalesmanPrint(self._current_source_sale, self._current_similar_sales)
            self._printing.print_box_plots()

    def __check_spacy_doc_similarity__(self, similar_sales: list):
        if self._salesman_spacy.sm_loaded:
            return
        my_sale_title_doc = self.nlp(self._current_source_sale.title)
        for similar_sale in similar_sales:
            similar_sale_title_doc = self.nlp(similar_sale.title)
            similarity = my_sale_title_doc.similarity(similar_sale_title_doc)
            similarity_text = self._salesman_spacy.get_similarity_text(similarity)
            if self.sys_config.print_details:
                print('Similarity between {} and {}: {} ({})'.format(
                    self._current_source_sale.title, similar_sale.title, similarity, similarity_text
                ))

    def __identify_outliers__(self, similar_sale_dict: dict):
        if len(similar_sale_dict) == 0:
            return
        price_single_list = [similar_sale.price_single for similar_sale in similar_sale_dict.values()]
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        for similar_sale in similar_sale_dict.values():
            similar_sale.set_is_outlier(True if outlier.is_value_outlier(similar_sale.price_single) else False)

    def __write_to_excel__(self, similar_sales: list):
        if not self.sys_config.write_to_excel:
            return
        row_list = []
        try:
            self._excel.start_iteration()
            if self._current_source_sale is None:
                source_sale_id = ''
                source_sale_title = ''
            else:
                source_sale_id = self._current_source_sale.sale_id
                source_sale_title = self._current_source_sale.title
                row_list.append(self._current_source_sale.get_value_dict_for_worksheet())
            for similar_sale in similar_sales:
                row_list.append(similar_sale.get_value_dict_for_worksheet(source_sale_id, source_sale_title))
            for idx, value_dict in enumerate(row_list):
                # print('value_dict={}'.format(value_dict))
                self._excel.add_row_by_value_dict(value_dict)
        finally:
            self._excel.print_message_after_iteration(len(row_list))

    def __get_excel__(self):
        if self.sys_config.write_to_excel:
            excel_obj = MyExcel(self.excel_file_path, sheet_name='Similar sales')
            excel_obj.write_header(SLDC.get_columns_for_excel())
            return excel_obj

    def __write_to_database__(self, sales: list, enforce_writing=False):
        self._sale_factory.write_sales_after_checks_to_db(sales, self._current_source_sale, enforce_writing)

    def __write_sale_to_database__(self, sale: SalesmanSale):
        self.__write_to_database__([sale], enforce_writing=True)

    def restrict_printing_to_selected_print_category(self, print_category: str):
        self._printing.init_for_selected_plot_categories([print_category])

    def __add_sale_to_database_input_list__(self, sale: SalesmanSale, input_list: list):
        if sale.is_sale_ready_for_sale_table():
            sale_dict = sale.get_data_dict_for_sale_table()
            sale_from_db = self._sale_factory.get_sale_from_db_by_sale_id(sale.sale_id)
            if sale_from_db is None:
                input_list.append(sale_dict)
            else:
                identical_check = SaleIdenticalCheck(sale, sale_from_db, number_from_db=2)
                today_str = MyDate.get_date_str_from_datetime()
                if identical_check.are_identical:
                    if sale_from_db.last_check_date != today_str:
                        self._sale_factory.update_last_check_date(sale_from_db, today_str)
                else:
                    sale_dict[SLDC.COMMENT] = 'Changes: {}'.format(identical_check.different_columns)
                    sale_dict[SLDC.START_DATE] = today_str  # we change the start date since some changes....
                    input_list.append(sale_dict)

    @staticmethod
    def __get_similar_sales_as_dict_list__(similar_sales: list, for_db=True) -> list:
        return_list = []
        for similar_sale in similar_sales:
            if for_db:
                if similar_sale.is_sale_ready_for_sale_table():
                    sale_dict = similar_sale.get_data_dict_for_sale_table()
                    return_list.append(sale_dict)
            else:
                return_list.append(
                    similar_sale.get_data_dict_for_columns(SLDC.get_columns_for_search_results()))
        return return_list

    def __get_my_virtual_sales__(self, number=0):
        self._sale_platform = 'virtual'
        tutti_sales = []
        virtual_sale_df = self.__get_sale_elements_from_file__()
        for idx, row in virtual_sale_df.iterrows():
            print('idx={} - row.title={}'.format(idx, row[SLDC.TITLE]))
            if number == 0 or idx == number - 1:
                sale = self._sale_factory.get_sale_by_file_row(row)
                tutti_sales.append(sale)
        return tutti_sales

    def __get_sale_elements_from_file__(self) -> pd.DataFrame:
        df = pd.read_csv(self.sys_config.virtual_sales_file_path, delimiter='#', header=None)
        df.columns = SLDC.get_columns_for_virtual_sales_in_file()
        return df

    def __visualize_dependencies__(self, sale: list):
        for sale in sale:
            doc_dict = {'Title': self.nlp(sale.title), 'Description': self.nlp(sale.description)}
            for key, doc in doc_dict.items():
                displacy.render(doc, style='dep')
                displacy.render(doc, style='ent')

    def __get_sales_on_platform_for_api__(self, api: SalesmanSearchApi):
        api.print_api_details('...inspect by api')
        self._sale_factory.adjust_web_parser_by_search_api(api)
        return self._sale_factory.get_sales_by_search_label_list([])

    def __get_similar_sales_for_sale__(self, sale: SalesmanSale) -> list:
        sale.compute_entity_based_search_lists()
        search_data = SalesmanSearchData(self.sys_config, sale)
        similar_sale_dict = {}
        for search_api in search_data.search_api_list:
            search_api.print_api_details('...looping')
            self._sale_factory.adjust_web_parser_by_search_api(search_api)
            for level in sale.search_levels[-1:]:
                print('sale.get_entity_based_search_lists({})={}'.format(level, sale.get_entity_based_search_lists(level)))
                for search_label_list in sale.get_entity_based_search_lists(level):
                    self.__get_sales_from_platform_for_search_label_list__(similar_sale_dict, search_label_list, sale)
                print('Elements in similar_sale_dict: {} after level {}'.format(len(similar_sale_dict), level))
                if len(similar_sale_dict) > 100:
                    break
        self.__identify_outliers__(similar_sale_dict)
        similar_sales_summary = [sale for sale in similar_sale_dict.values()]
        if self.sys_config.print_details:
            self.__print_similar_sales__(sale, similar_sales_summary)
        return similar_sales_summary

    def __get_sales_from_platform_for_search_label_list__(
            self, similar_sales_dict: dict, search_label_list: list, sale: SalesmanSale):
        similar_sales = self._sale_factory.get_sales_by_search_label_list(search_label_list)
        for similar_sale in similar_sales:
            if self.__can_similar_sale_be_added_to_dict__(similar_sales_dict, sale, similar_sale):
                similar_sale.set_master_details(sale.sale_id, sale.title)
                similar_sales_dict[similar_sale.sale_id] = similar_sale

    @staticmethod
    def __can_similar_sale_be_added_to_dict__(similar_dict: dict, sale: SalesmanSale, similar_sale: SalesmanSale):
        if similar_sale.sale_id == sale.sale_id:
            return False
        sale_similarity_check = SaleSimilarityCheck(sale, similar_sale)
        if not sale_similarity_check.are_sales_similar:
            print('\nSource sale {} "{}" is not similar to found sale {} "{}" - label: {}'.format(
                sale.sale_id, sale.title, similar_sale.sale_id, similar_sale.title, sale_similarity_check.similar_label))
            print('--> entity_dict source: {}'.format(sale.get_entity_label_main_values_dict_as_string()))
            print('--> entity_dict check: {}'.format(similar_sale.get_entity_label_main_values_dict_as_string()))
            return False
        if similar_sale.sale_id not in similar_dict:  # similar sale was not added so far
            return True
        return len(similar_sale.found_by_labels) > len(similar_dict[similar_sale.sale_id].found_by_labels)

    @staticmethod
    def __print_similar_sales__(sale, similar_sales: list):
        sale.print_sale_in_original_structure()
        if len(similar_sales) == 0:
            print('\nNO SIMILAR SALES AVAILABLE for {}'.format(sale.key))
        for sale in similar_sales:
            sale.print_sale_in_original_structure()

    @staticmethod
    def __get_sale_platform__():
        return SLSRC.TUTTI_CH

