"""
Description: This module contains the tab for Dash for pattern statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from pattern_dash.my_dash_base import MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyDCC, MyHTML
from dash import Dash


class MyDashTab4PatternStatistics(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyDashBaseTab.__init__(self, app, sys_config)
        self._df_features_records = self.sys_config.db_stock.get_features_records_as_dataframe()
        self._features_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_features_records)

    def get_div_for_tab(self):
        header = MyHTML.h1('This is the content in tab 4: Features statistics')
        paragraph = MyHTML.p('A graph here would be nice!')
        drop_down = self.__get_drop_down_for_features__()
        table = self.__get_table_for_features__(5)
        return MyHTML.div('my_statistics', [header, paragraph, drop_down, table])

    @staticmethod
    def __get_drop_down_for_features__():
        options = [{'label': 'df', 'value': 'df'}]
        return MyDCC.drop_down('features-selection', options)

    def __get_table_for_features__(self, number=5):
        return MyDCC.data_table('features_table', self._features_rows_for_data_table[:number], min_height=200)