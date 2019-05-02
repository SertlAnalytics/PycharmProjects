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


class SalesmanPrint:
    def __init__(self, column_list: list):
        self._column_list = column_list
        self._sale_dict_list = []
        self._df_sale = self.__get_df_from_sale_list__()

    def init_by_sale_dict(self, sale_dict_list: list):
        self._sale_dict_list = sale_dict_list
        self._df_sale = self.__get_df_from_sale_list__()
        self._df_sale = self.__get_df_without_single_entries__()

    @property
    def df_sale(self):
        return self._df_sale

    @property
    def columns(self):
        return self._column_list

    def __get_df_from_sale_list__(self):
        return pd.DataFrame.from_dict(
            {col: [sale_dict[col] for sale_dict in self._sale_dict_list] for col in self._column_list}
        )

    def __get_df_without_single_entries__(self):
        category_list = self._df_sale[SLDC.PRINT_CATEGORY].unique()
        category_remove_list = []
        # print('category_list={}'.format(category_list))
        for print_category in category_list:
            df = self._df_sale[self._df_sale[SLDC.PRINT_CATEGORY] == print_category]
            if df.shape[0] <= 1:
                category_remove_list.append(print_category)
        if len(category_remove_list) > 0:
            return self._df_sale[self._df_sale[SLDC.PRINT_CATEGORY].isin(category_remove_list) == False]
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
        g = sns.swarmplot(y=SLDC.PRINT_CATEGORY,
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
        b = sns.boxplot(y=SLDC.PRINT_CATEGORY,
                        x=SLDC.PRICE_SINGLE,
                        data=self._df_sale, whis=np.inf)
        g = sns.swarmplot(y=SLDC.PRINT_CATEGORY,
                          x=SLDC.PRICE_SINGLE,
                          data=self._df_sale,
                          # Decrease the size of the points to avoid crowding
                          size=7, color='black')
        # remove the top and right line in graph
        # self.__add_annotation__()
        sns.despine()
        g.figure.set_size_inches(12, 8)
        plt.show()

    def __add_annotation__(self):
        # Annotate. xy for coordinate. max_wage is x and 0 is y. In this plot y ranges from 0 to 7 for each level
        # xytext for coordinates of where I want to put my text
        max_price = self._df_sale[SLDC.PRICE_SINGLE].max()
        max_price_title = self._df_sale[(self._df_sale[SLDC.PRICE_SINGLE] == max_price)][SLDC.TITLE].values[0]
        plt.annotate(s=max_price_title,
                     xy=(max_price, 0),
                     xytext=(max_price * 0.8, -0.2),
                     # Shrink the arrow to avoid occlusion
                     arrowprops={'facecolor': 'gray', 'width': 1, 'shrink': 0.03},
                     backgroundcolor='white')
