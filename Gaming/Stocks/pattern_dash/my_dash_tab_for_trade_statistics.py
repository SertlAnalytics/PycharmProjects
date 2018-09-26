"""
Description: This module contains the tab for Dash for trade statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

import plotly.graph_objs as go
import pandas as pd
from pattern_dash.my_dash_base import MyDashBase, MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import MyDCC, MyHTML, DccGraphApi
from dash import Dash


class MyDashTab4TradeStatistics(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyDashBaseTab.__init__(self, app, sys_config)
        self._df_trade_records = self.sys_config.db_stock.get_trade_records_as_dataframe()
        self._trade_rows_for_data_table = MyDCC.get_rows_from_df_for_data_table(self._df_trade_records)

    def get_div_for_tab(self):
        header = MyHTML.h1('This is the content in tab 3: Trade statistics')
        paragraph = MyHTML.p('A graph here would be nice!')
        drop_down = self.__get_drop_down_for_trades__()
        table = self.__get_table_for_trades__()
        scatter_graph = self.__get_scatter_graph_for_trades__()
        return MyHTML.div('my_trade_statistics', [header, paragraph, drop_down, table, scatter_graph])

    @staticmethod
    def __get_drop_down_for_trades__(drop_down_name='trades-selection_statistics'):
        options = [{'label': 'df', 'value': 'df'}]
        return MyDCC.drop_down(drop_down_name, options)

    def __get_table_for_trades__(self, table_name='trade_table', number=5):
        return MyDCC.data_table(table_name, self._trade_rows_for_data_table[:number], min_height=200)

    def __get_scatter_graph_for_trades__(self, scatter_graph_id='trade_statistics_scatter_graph'):
        graph_api = DccGraphApi(scatter_graph_id, 'My Trades')
        graph_api.figure_data = self.__get_scatter_figure_data_for_trades__(self._df_trade_records)
        return MyDCC.graph(graph_api)

    @staticmethod
    def __get_scatter_figure_data_for_trades__(df: pd.DataFrame):
        return [
            go.Scatter(
                x=df[df['Pattern_Type'] == i]['Forecast_Full_Positive_PCT'],
                y=df[df['Pattern_Type'] == i]['Trade_Result_ID'],
                text=df[df['Pattern_Type'] == i]['Trade_Strategy'],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ) for i in df.Pattern_Type.unique()
        ]
