"""
Description: This module contains the tab for Dash for trade statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-26
"""

from dash.dependencies import Input, Output, State
from sertl_analytics.constants.pattern_constants import DC, TRC, EQUITY_TYPE
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration
from dash import Dash
from pattern_trade_handler import PatternTradeHandler
from pattern_dash.my_dash_colors import DashColorHandler
from pattern_database.stock_tables import AssetTable
from pattern_dash.my_dash_header_tables import MyHTMLTabAssetStatisticsHeaderTable
from pattern_dash.my_dash_tab_dd_for_statistics import AssetStatisticsDropDownHandler
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Assets
from pattern_dash.my_dash_tab_for_statistics_base import MyDashTab4StatisticsBase, DDT
from sertl_analytics.mydash.my_dash_components import MyHTML
import pandas as pd
import numpy as np


class MyDashTab4AssetStatistics(MyDashTab4StatisticsBase):
    def __init__(self, app: Dash, sys_config: SystemConfiguration,
                 color_handler: DashColorHandler, trade_handler_online: PatternTradeHandler):
        self._trade_handler_online = trade_handler_online
        MyDashTab4StatisticsBase.__init__(self, app, sys_config, color_handler)
        self._total_assets_start_dict = {}
        self._total_assets_latest_dict = {}
        self._total_assets_start_timestamp_dict = {}
        self.__fill_total_assets_dictionaries__()
        self._trade_number_dict = {}
        self.__fill_trade_number_dict__()

    def __fill_tab__(self):
        self._tab = 'asset'

    @property
    def column_result(self):
        return DC.VALUE_TOTAL

    def init_callbacks(self):
        self.__init_callback_for_numbers__()
        # self.__init_callback_for_pattern_type_label__()
        # self.__init_callback_for_pattern_type_numbers__()
        # self.__init_callbacks_for_drop_down_visibility__()
        self.__init_callbacks_for_chart__()
        # self.__init_callback_for_markdown__()
        # self.__init_callback_for_x_variable_options__()
        # self.__init_callback_for_y_variable_options__()
        pass

    def get_div_for_tab(self):
        children_list = [
            self.__get_html_tab_header_table__(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TYPE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.X_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.Y_VARIABLE)),
            # MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TEXT_VARIABLE)),
            MyHTML.div(self._my_statistics_chart_div, self.__get_charts_from_plotter__(), False),
        ]
        # print('self._my_statistics_chart_div={}'.format(self._my_statistics_chart_div))
        return MyHTML.div(self._my_statistics, children_list)

    def __init_callback_for_numbers__(self):
        @self.app.callback(
            Output('my_asset_crypto_client_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_crypto_client_assets(n_intervals: int):
            amount, change_abs, change_pct = self.__get_asset_numbers_for_trade_client__(TRC.BITFINEX)
            return '{:.0f} ({:+.0f}/{:+.2f}%)'.format(amount, change_abs, change_pct)

        @self.app.callback(
            Output('my_asset_stock_client_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_stock_client_assets(n_intervals: int):
            amount, change_abs, change_pct = self.__get_asset_numbers_for_trade_client__(TRC.IBKR)
            return '{:.0f} ({:+.0f}/{:+.2f}%)'.format(amount, change_abs, change_pct)

        @self.app.callback(
            Output('my_asset_crypto_client_trades_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_crypto_client_trades(n_intervals: int):
            trades = self._trade_number_dict[TRC.BITFINEX]
            return '+{:d}/-{:d}'.format(trades[0], trades[1])

        @self.app.callback(
            Output('my_asset_stock_client_trades_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_crypto_client_trades(n_intervals: int):
            trades = self._trade_number_dict[TRC.IBKR]
            return '+{:d}/-{:d}'.format(trades[0], trades[1])

    def __init_callbacks_for_chart__(self):
        @self.app.callback(
            Output(self._my_statistics_chart_div, 'children'),
            [Input(self._my_statistics_chart_type_selection, 'value'),
             Input(self._my_statistics_category_selection, 'value'),
             Input(self._my_statistics_x_variable_selection, 'value'),
             Input(self._my_statistics_y_variable_selection, 'value'),
             # Input(self._my_statistics_text_variable_selection, 'value'),
             Input('my_interval_refresh', 'n_intervals')])
        def handle_callbacks_for_asset_chart(ct: str, category: str, x: str, y: str, n_intervals: int):
            self.__fill_df_base__()
            self.__init_plotter__()
            self._plotter.chart_type = ct
            self._plotter.category = category
            self._plotter.x_variable = x
            self._plotter.y_variable = y
            return self.__get_charts_from_plotter__()

    def __get_asset_numbers_for_trade_client__(self, trade_client: str):
        amount_start = self._total_assets_start_dict[trade_client]
        amount_current = self.__get_total_assets_latest__(trade_client)
        change_abs = amount_current - amount_start
        change_pct = 0 if amount_start == 0 else (amount_current/amount_start - 1) * 100
        return amount_current, change_abs, change_pct

    def __fill_total_assets_dictionaries__(self):
        for trade_client in [TRC.BITFINEX, TRC.IBKR]:
            df_with_client = self._df_base[self._df_base[DC.LOCATION] == trade_client]
            if df_with_client.shape[0] == 0:
                self._total_assets_start_dict[trade_client] = 0
                self._total_assets_latest_dict[trade_client] = 0
                self._total_assets_start_timestamp_dict[trade_client] = MyDate.get_epoch_seconds_from_datetime()
            else:
                df_with_client.sort_values(by=[DC.VALIDITY_TS])
                grouped_series = df_with_client.groupby([DC.VALIDITY_TS])[DC.VALUE_TOTAL].sum()
                self._total_assets_start_dict[trade_client] = grouped_series.iloc[0]
                self._total_assets_latest_dict[trade_client] = grouped_series.iloc[grouped_series.shape[0]-1]
                self._total_assets_start_timestamp_dict[trade_client] = grouped_series.index[0]

    def __get_total_assets_latest__(self, trade_client: str):
        amount_current = self._trade_handler_online.get_balance_total()
        return self._total_assets_latest_dict[trade_client] if amount_current == 0 else amount_current

    def __fill_trade_number_dict__(self):
        df_trades = self.sys_config.db_stock.get_trade_records_for_asset_statistics_as_dataframe()
        for trade_client in [TRC.BITFINEX, TRC.IBKR]:
            self._trade_number_dict[trade_client] = [0, 0]  # default
            if df_trades.shape[0] > 0:
                equity_type = EQUITY_TYPE.CRYPTO if trade_client == TRC.BITFINEX else EQUITY_TYPE.SHARE
                ts_from = self._total_assets_start_timestamp_dict[trade_client]
                # ts_from = 1530482400
                df_with_trades = df_trades[np.logical_and(
                    df_trades[DC.EQUITY_TYPE] == equity_type, df_trades[DC.TS_PATTERN_TICK_FIRST] > ts_from)]
                if df_with_trades.shape[0] > 0:
                    df_pos = df_with_trades[df_with_trades[DC.TRADE_RESULT_ID] == 1]
                    df_neg = df_with_trades[df_with_trades[DC.TRADE_RESULT_ID] == -1]
                    self._trade_number_dict[trade_client] = [df_pos.shape[0], df_neg.shape[0]]

    def __get_df_trades__(self) -> pd.DataFrame:
        return self.sys_config.db_stock.get_trade_records_for_asset_statistics_as_dataframe()

    @staticmethod
    def __get_html_tab_header_table__():
        return MyHTMLTabAssetStatisticsHeaderTable().get_table()

    def __get_df_base__(self) -> pd.DataFrame:
        df_from_db = self.sys_config.db_stock.get_asset_records_for_statistics_as_dataframe()
        df_from_balance = self._trade_handler_online.get_balance_as_asset_data_frame()
        if df_from_balance is None:
            return df_from_db
        df_concat = pd.concat([df_from_db, df_from_balance])
        df_concat.reset_index(inplace=True)
        return df_concat

    def __init_dd_handler__(self):
        self._dd_handler = AssetStatisticsDropDownHandler()

    def __init_plotter__(self):
        self._plotter = MyDashTabStatisticsPlotter4Assets(
            self._df_base, self._color_handler, self._trade_handler_online)

    @staticmethod
    def __get_value_list_for_x_variable_options__(chart_type: str, predictor: str):
        return AssetTable.get_columns_for_statistics_x_variable()

    @staticmethod
    def __get_value_list_for_y_variable_options__(chart_type: str, predictor: str):
        return AssetTable.get_columns_for_statistics_y_variable()
