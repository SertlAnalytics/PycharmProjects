"""
Description: This module is the base plotting class for Salesman application.
Author: Josef Sertl
Copyright: https://towardsdatascience.com/3-awesome-visualization-techniques-for-every-dataset-9737eecacbe8
Date: 2019-04-28
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sertl_analytics.constants.salesman_constants import SLDC
from salesman_sale import SalesmanSale
from entities.salesman_entity_handler import SalesmanEntityHandler


class SalesmanPrint:
    def __init__(self, sale_source: SalesmanSale, sales: list):
        self._entity_handler = sale_source.sys_config.entity_handler
        self._columns = SLDC.get_columns_for_sales_plotting()
        self._sale_source = sale_source
        self._sales = sales
        self._sale_dict_list = []
        self.__fill_sale_dict_list__()
        self._df_sale = self.__get_df_from_sale_dict_list__(self._sale_dict_list)
        self._df_sale = self.__get_df_without_single_entries__()
        self._plot_category_list = self._df_sale[SLDC.PLOT_CATEGORY].unique()
        self._detail_offset_dict = {}
        self._ax = None

    @property
    def plot_category_list(self):
        return self._plot_category_list

    @property
    def df_sale(self):
        return self._df_sale

    @property
    def columns(self):
        return self._columns

    def init_for_selected_plot_categories(self, category_list: list):
        selected_category_list = self._plot_category_list if category_list is None else category_list
        dict_list = [sale_dict for sale_dict in self._sale_dict_list
                     if sale_dict[SLDC.PLOT_CATEGORY] in selected_category_list or len(category_list) == 0]
        self._df_sale = self.__get_df_from_sale_dict_list__(dict_list)

    def __fill_sale_dict_list__(self):
        for label, main_values in self._sale_source.entity_label_main_values_dict.items():
            print('__fill_sale_dict_list__: label={}, values={}'.format(label, main_values))
            for main_value in main_values:
                self.__add_to_sale_dict_list__(label, main_value)

    def __add_to_sale_dict_list__(self, entity_label: str, label_value: str):
        if self._sale_source.location != 'online':
            self._sale_source.set_value(SLDC.PLOT_CATEGORY, '{}_{}'.format(label_value, entity_label))
            self._sale_dict_list.append(self._sale_source.get_data_dict_for_columns(self._columns))
        for sale in self._sales:
            sale.set_value(SLDC.PLOT_CATEGORY, '{}_{}'.format(label_value, entity_label))
            self._sale_dict_list.append(sale.get_data_dict_for_columns(self._columns))

    def __get_df_from_sale_dict_list__(self, sale_dict_list: list):
        return pd.DataFrame.from_dict(
            {col: [sale_dict[col] for sale_dict in sale_dict_list] for col in self._columns}
        )

    def __get_df_without_single_entries__(self):
        category_list = self._df_sale[SLDC.PLOT_CATEGORY].unique()
        category_remove_list = []
        for category in category_list:
            df = self._df_sale[self._df_sale[SLDC.PLOT_CATEGORY] == category]
            if df.shape[0] <= 1:
                category_remove_list.append(category)
        if len(category_remove_list) > 0:
            return self._df_sale[self._df_sale[SLDC.PLOT_CATEGORY].isin(category_remove_list) == False]
        return self._df_sale

    def print_sales_head(self):
        print(self._df_sale.head(5))

    def print_swarm_plot(self):
        if self._df_sale.shape[0] == 0:
            return
        """
         filtered_df = player_df[(player_df['Club'].isin(['FC Barcelona', 'Paris Saint-Germain',
                                                                'Manchester United', 'Manchester City', 'Chelsea',
                                                                'Real Madrid', 'FC Porto', 'FC Bayern München'])) &
                                       (player_df['Nationality'].isin(['England', 'Brazil', 'Argentina',
                                                                       'Brazil', 'Italy', 'Spain', 'Germany']))
                                                                       ]
        :return:
        """
        g = sns.swarmplot(y=SLDC.PLOT_CATEGORY,
                          x=SLDC.PRICE_SINGLE,
                          data=self._df_sale,
                          # Decrease the size of the points to avoid crowding
                          size=7)
        # remove the top and right line in graph
        sns.despine()
        g.figure.set_size_inches(14, 10)
        plt.show()

    def print_box_plots(self):
        if self._df_sale.shape[0] == 0:
            return
        b = sns.boxplot(y=SLDC.PLOT_CATEGORY,
                        x=SLDC.PRICE_SINGLE,
                        data=self._df_sale, whis=np.inf)
        self._ax = sns.swarmplot(y=SLDC.PLOT_CATEGORY,
                                 x=SLDC.PRICE_SINGLE,
                                 data=self._df_sale,
                                 # Decrease the size of the points to avoid crowding
                                 size=7, color='black')
        # remove the top and right line in graph
        # self.__add_annotation__()
        sns.despine()
        self._ax.figure.set_size_inches(12, 8)
        self._ax.figure.canvas.mpl_connect('button_press_event', self.__on_click__)
        self._ax.figure.canvas.mpl_connect('motion_notify_event', self.__on_motion_notify__)
        self._ax.axes.format_coord = self.__on_hover__
        self.__init_detail_offset_dict__(self._ax.axes)
        plt.show()

    def __init_detail_offset_dict__(self, axes):
        for idx, print_category in enumerate(self._plot_category_list):
            offsets = axes.collections[idx].get_offsets()
            # print('type(offsets)={}, offsets={}'.format(type(offsets), offsets))
            row_detail_list = self.__get_row_detail_list_for_print_category__(print_category)
            for idx, offsets in enumerate(axes.collections[idx].get_offsets()):
                detail = '{}: {}'.format(print_category, row_detail_list[idx])
                self._detail_offset_dict[detail] = offsets
        # print('__init_detail_offset_dict__={}'.format(self._detail_offset_dict))

    def __get_row_detail_list_for_print_category__(self, category: str) -> list:
        row_detail_list = []
        df_plot_category = self._df_sale[self._df_sale[SLDC.PLOT_CATEGORY] == category]
        df_plot_category = df_plot_category.sort_values(by=SLDC.PRICE_SINGLE)
        for i in range(df_plot_category.shape[0]):
            row = df_plot_category.iloc[i]
            row_detail = '{}: {:.2f} CHF'.format(row[SLDC.TITLE], row[SLDC.PRICE_SINGLE])
            row_detail_list.append(row_detail)
        return row_detail_list

    def __add_annotation__(self):
        # Annotate. xy for coordinate. max_wage is x and 0 is y. In this plot y ranges from 0 to 7 for each level
        # xytext for coordinates of where I want to put my text
        max_price = self._df_sale[SLDC.PRICE_SINGLE].max()
        max_price_title = \
            self._df_sale[(self._df_sale[SLDC.PRICE_SINGLE] == max_price)][SLDC.TITLE].values[0]
        plt.annotate(s=max_price_title,
                     xy=(max_price, 0),
                     xytext=(max_price * 0.8, -0.2),
                     # Shrink the arrow to avoid occlusion
                     arrowprops={'facecolor': 'gray', 'width': 1, 'shrink': 0.03},
                     backgroundcolor='white')

    def __on_motion_notify__(self, event):
        # self.__reset_patch_lists__(event)
        # self.__handle_visibility_for_range_polygons__(event)
        # self.__handle_visibility_for_fibonacci_waves__(event)
        self.__print_current_selected_patch__(event)

    def __on_click__(self, event):
        self.__print_current_selected_patch__(event)

    def __print_current_selected_patch__(self, event):
        for patches in self._ax.patches:
            cont, dic = patches.contains(event)
            if cont:
                print(patches)

    def __on_hover__(self, x, y):
        dist_y = 0.3
        dist_x = 1
        for detail, offset in self._detail_offset_dict.items():
            if x - dist_x < offset[0] < x + dist_x:
                if y - dist_y < offset[1] < y + dist_y:
                    return detail
        return '{} --> {:.2f} CHF'.format(self.__get_print_category_for_y_coordinate__(y), x)

    def __get_print_category_for_y_coordinate__(self, y: float):
        y_idx = int(y + 0.5)
        if 0 <= y_idx < len(self._plot_category_list):
            return self._plot_category_list[y_idx]
        return 'Price single'





