"""
Description: This module contains a container for list of sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-23
"""

from sertl_analytics.constants.salesman_constants import SLDC
from entities.salesman_named_entity import SalesmanEntityHandler
from salesman_system_configuration import SystemConfiguration
import pandas as pd
from salesman_sale import SalesmanSale
from sertl_analytics.my_pandas import MyPandas
from calculation.outlier import Outlier


class SalesmanSaleList:
    def __init__(self, sys_config: SystemConfiguration, sales: list, sale_source: SalesmanSale):
        self.sys_config = sys_config
        self._sales = sales
        self._sales.sort()
        self._sale_source = sale_source
        self.__identify_outliers_for_sales__()
        self._columns_for_search_results = SLDC.get_columns_for_search_results()
        self._columns_for_plotting = SLDC.get_columns_for_sales_plotting()
        self._sale_dict_list_for_result = \
            [sale.get_data_dict_for_columns(self._columns_for_search_results) for sale in self._sales]
        self._sale_dict_list_for_plotting = []
        self.__init_sale_dict_list_for_plotting__(self._sale_source)
        self._df_for_plotting = self.__get_df_for_plotting__()

    @property
    def plot_categories(self) -> list:
        category_list = self._df_for_plotting[SLDC.PLOT_CATEGORY].unique()
        category_list.sorted()
        return category_list

    def get_sales_as_search_result_rows(self):
        return [sale.get_data_dict_for_columns(self._columns_for_search_results) for sale in self._sales]

    def get_sales_as_search_result_rows_for_selected_plot_categories(self, selected_plot_categories: list):
        if selected_plot_categories is None or len(selected_plot_categories) == 0:
            return self.get_sales_as_search_result_rows()
        return_list = []
        for sale in self._sales:
            is_valid_for_selection = True
            entity_label_dict = sale.get_value(SLDC.ENTITY_LABELS_DICT)
            for selected_plot_category in selected_plot_categories:
                if entity_label_dict.get(selected_plot_category[1], '') != selected_plot_category[0]:
                    is_valid_for_selection = False
                    break
            if is_valid_for_selection:
                return_list.append(sale.get_data_dict_for_columns(self._columns_for_search_results))
        return return_list

    def __get_df_for_plotting__(self):
        df = self.__get_df_from_sale_dict_list_for_plotting__()
        return MyPandas.get_df_reduced_regarding_category_numbers(df, SLDC.PLOT_CATEGORY, 1)

    def __init_sale_dict_list_for_plotting__(self, sale_source: SalesmanSale):
        self._sale_dict_list_for_plotting = []
        for label_value, entity_label in sale_source.entity_label_dict.items():
            print('__fill_sale_dict_list__: label={}, value={}'.format(entity_label, label_value))
            if SalesmanEntityHandler.get_main_entity_name_for_entity_name(entity_label, label_value) == label_value:
                self.__add_to_sale_dict_list_for_plotting__(entity_label, label_value)

    def __add_to_sale_dict_list_for_plotting__(self, entity_label: str, label_value: str):
        # we repeat entries for a sale for different plot categories
        plot_category = self.__get_plot_category_for_label_and_value__(entity_label, label_value)
        for sale in self._sales:
            if entity_label == sale.entity_label_dict.get(label_value, ''):
                sale.set_value(SLDC.PLOT_CATEGORY, plot_category)
                self._sale_dict_list_for_plotting.append(sale.get_data_dict_for_columns(self._columns_for_plotting))

    def __get_df_from_sale_dict_list_for_plotting__(self):
        columns = self._columns_for_plotting
        data_dict = self._sale_dict_list_for_plotting
        return pd.DataFrame.from_dict({col: [sale_dict[col] for sale_dict in data_dict] for col in columns})

    @staticmethod
    def __get_plot_category_for_label_and_value__(entity_label: str, label_value: str):
        return '{}: {}'.format(entity_label, label_value)

    def __identify_outliers_for_sales__(self):
        if len(self._sales) == 0:
            return
        price_single_list = [sale.price_single for sale in self._sales]
        outlier = Outlier(price_single_list, self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        for sale in self._sales:
            sale.set_is_outlier(True if outlier.is_value_outlier(sale.price_single) else False)

