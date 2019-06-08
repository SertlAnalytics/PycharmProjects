"""
Description: This module handles the results which are shown in grids and as plotter
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-23
"""

from sertl_analytics.constants.salesman_constants import SLDC, OUTHDL
from salesman_system_configuration import SystemConfiguration
import pandas as pd
from salesman_sale import SalesmanSale
import numpy as np
from calculation.outlier import Outlier


class SalesmanResultDataHandler:
    """
    This data frame serves different purposes:
    1. Restrict the base DataFrame to the selected criteria
    2. Calculates the outliers for this selection set
    This will be accomplished by adding two columns to the dataframe
    a) Plot_Category
    b) Is_Outlier
    Concept behind this: We assume that operations on a df (logical_and, ...)
    is quite faster then handling rows separately.
    """
    def __init__(self, sys_config: SystemConfiguration, df: pd.DataFrame,):
        self._columns_for_similar_sale_grid = SLDC.get_columns_for_similar_sales_tab_table()
        self._columns_for_plotting = SLDC.get_columns_for_sales_plotting()
        self.sys_config = sys_config
        self._df_base = df
        self.__assign_process_columns_to_data_frame__()
        self._sale_master = None
        self._df_for_sale_master = None
        self._entity_label_main_values_dict = {}
        self._df_for_grid = None
        self._df_for_plot = None
        self._outlier_for_selection = None

    @property
    def plot_categories(self) -> list:
        category_list = []
        for label, values in self._entity_label_main_values_dict.items():
            for value in values:
                category_list.append('{}#{}'.format(value, label))
        category_list.sort()
        return category_list

    @property
    def sale_master(self) -> SalesmanSale:
        return self._sale_master

    @property
    def df_for_grid(self) -> pd.DataFrame:
        return self._df_for_grid

    @property
    def df_for_plot(self) -> pd.DataFrame:
        return self._df_for_plot

    @property
    def outlier_for_selection(self) -> Outlier:
        return self._outlier_for_selection

    def init_by_sale_master(self, sale_master: SalesmanSale):
        if self._sale_master is not None and self._sale_master.sale_id == sale_master.sale_id:
            return
        print('init_by_sale_master: master_sale_id={}'.format(sale_master.sale_id))
        self._sale_master = sale_master
        self._df_for_sale_master = pd.DataFrame(self._df_base[self._df_base[SLDC.MASTER_ID] == sale_master.sale_id])
        self._df_for_sale_master.sort_values([SLDC.SALE_ID, SLDC.VERSION])
        self._entity_label_main_values_dict = sale_master.entity_label_main_values_dict
        self.__calculate_plot_categories_for_df_for_source__()

    def adjust_result_to_selected_entities(self, selected_entities: list):
        print('adjust_result_to_selected_entities: selected_entities={}'.format(selected_entities))
        df_result = pd.DataFrame(self._df_for_sale_master)
        print('...before adjustment: df_result.shape={}'.format(df_result.shape))
        plot_categories = list(df_result[SLDC.PLOT_CATEGORY].unique())
        print('plot_categories={}'.format(plot_categories))
        for selected_entity in selected_entities:
            print('selected_entity={}'.format(selected_entity))
            df_result = df_result[df_result[SLDC.PLOT_CATEGORY].str.contains(selected_entity)]
            print('...after adjustment: df_result.shape={}'.format(df_result.shape))
        if df_result.shape[0] == 0:
            self._df_for_grid = None
            self._df_for_plot = None
        else:
            df_result = df_result.sort_values([SLDC.SALE_ID, SLDC.VERSION])
            self.__identify_outliers_in_dataframe__(df_result)
            self._df_for_grid = df_result[self._columns_for_similar_sale_grid]
            self._df_for_plot = self.__get_df_for_plot__(df_result)

    # def __get_df_for_plotting__(self, df_base: pd.DataFrame):
    #     return MyPandas.get_df_reduced_regarding_category_numbers(df, SLDC.PLOT_CATEGORY, 1)

    def __get_df_for_plot__(self, df_result: pd.DataFrame) -> pd.DataFrame:
        df_for_plot = df_result[self._columns_for_plotting]
        outlier = self._outlier_for_selection
        if self.sys_config.outlier_handling_for_plot == OUTHDL.CUT_IQR:
            df_for_plot = df_for_plot[np.logical_and(df_for_plot[SLDC.PRICE_SINGLE] >= outlier.bottom_threshold_iqr,
                                                     df_for_plot[SLDC.PRICE_SINGLE] <= outlier.top_threshold_iqr)]
        elif self.sys_config.outlier_handling_for_plot == OUTHDL.CUT_CONFIGURED:
            df_for_plot = df_for_plot[np.logical_and(df_for_plot[SLDC.PRICE_SINGLE] >= outlier.bottom_threshold,
                                                     df_for_plot[SLDC.PRICE_SINGLE] <= outlier.top_threshold)]
        return df_for_plot

    @staticmethod
    def __get_plot_category_for_label_and_value__(entity_label: str, label_value: str):
        return '{}#{}'.format(label_value, entity_label)

    def __assign_process_columns_to_data_frame__(self):
        if SLDC.IS_OUTLIER not in self._df_base.columns:
            self._df_base.assign(Is_outlier=0)
        if SLDC.PLOT_CATEGORY not in self._df_base.columns:
            self._df_base.assign(Plot_Category='')

    def __calculate_plot_categories_for_df_for_source__(self):
        self._df_for_sale_master[SLDC.PLOT_CATEGORY] = \
            self._df_for_sale_master[SLDC.ENTITY_LABELS_DICT].apply(
                self.__calculate_plot_category_for_entity_label_dict_as_string__)

    def __calculate_plot_category_for_entity_label_dict_as_string__(self, entity_label_dict_str: str):
            entry_list = []
            for label, values in self._entity_label_main_values_dict.items():
                for value in values:
                    value_label_entry = '{} ({})'.format(value, label)
                    if entity_label_dict_str.find(value_label_entry) > -1:
                        entry_list.append(self.__get_plot_category_for_label_and_value__(label, value))
            return ', '.join(entry_list)

    def __identify_outliers_in_dataframe__(self, df: pd.DataFrame):
        if df.shape[0] == 0:
            return
        self._outlier_for_selection = Outlier(list(df[SLDC.PRICE_SINGLE]), self.sys_config.outlier_threshold)
        # outlier.print_outlier_details()
        if self.sys_config.outlier_handling_for_plot == OUTHDL.CUT_IQR:
            df[SLDC.IS_OUTLIER] = df[SLDC.PRICE_SINGLE].apply(self._outlier_for_selection.is_value_iqr_outlier)
        else:
            df[SLDC.IS_OUTLIER] = df[SLDC.PRICE_SINGLE].apply(self._outlier_for_selection.is_value_outlier)

