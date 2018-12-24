"""
Description: This module contains the tab for Dash for pattern statistics.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash.dependencies import Input, Output, State
from pattern_dash.my_dash_base import MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from dash import Dash
from sertl_analytics.constants.pattern_constants import CHT, FT, DC
from pattern_dash.my_dash_components import MyHTML
from pattern_dash.my_dash_header_tables import MyHTMLTabPatternStatisticsHeaderTable
from pattern_dash.my_dash_tab_dd_for_statistics import DDT, PatternStatisticsDropDownHandler
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Pattern
from pattern_dash.my_dash_colors import DashColorHandler
from textwrap import dedent
from pattern_database.stock_tables import PatternTable
import pandas as pd


class MyDashTab4StatisticsBase(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, color_handler: DashColorHandler):
        MyDashBaseTab.__init__(self, app, sys_config)
        self._color_handler = color_handler
        self.__fill_tab__()
        self._df_base = None
        self.__fill_df_base__()
        self.__manipulate_ptc_columns__()
        self.__init_dash_element_ids__()
        self._plotter = None
        self.__init_plotter__()
        self.__init_dd_handler__()

    @property
    def column_result(self):
        return

    def get_div_for_tab(self):
        children_list = [
            self.__get_html_tab_header_table__(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TYPE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.PREDICTOR)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.X_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.Y_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TEXT_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.PATTERN_TYPE)),
            MyHTML.div(self._my_statistics_chart_div, self.__get_charts_from_plotter__(), False),
        ]
        return MyHTML.div(self._my_statistics, children_list)

    def __get_charts_from_plotter__(self):
        charts = self._plotter.get_chart_list()
        # print('charts = {}'.format(charts))
        if len(charts) == 1:
            return charts[0]
        embedded_element_list = []
        for chart in charts:
            embedded_element_list.append(MyHTML.div('HALLO', chart, inline=True))
        return MyHTML.div_embedded(embedded_element_list)

    def __fill_tab__(self):
        self._tab = 'base'

    @staticmethod
    def __get_html_tab_header_table__():
        return MyHTMLTabPatternStatisticsHeaderTable().get_table()

    def __init_dash_element_ids__(self):
        self._my_statistics_chart_type_div = 'my_{}_statistics_chart_type_div'.format(self._tab)
        self._my_statistics_markdown = 'my_{}_statistics_markdown'.format(self._tab)
        self._my_statistics_div = 'my_{}_statistics_div'.format(self._tab)
        self._my_statistics_detail_label_div = 'my_{}_statistics_detail_label_div'.format(self._tab)
        self._my_statistics_detail_div = 'my_{}_statistics_detail_div'.format(self._tab)
        self._my_statistics_chart_type_selection = 'my_{}_statistics_chart_type_selection'.format(self._tab)
        self._my_statistics_predictor_selection = 'my_{}_statistics_predictor_selection'.format(self._tab)
        self._my_statistics_category_selection = 'my_{}_statistics_category_selection'.format(self._tab)
        self._my_statistics_x_variable_selection = 'my_{}_statistics_x_variable_selection'.format(self._tab)
        self._my_statistics_y_variable_selection = 'my_{}_statistics_y_variable_selection'.format(self._tab)
        self._my_statistics_text_variable_selection = 'my_{}_statistics_text_variable_selection'.format(self._tab)
        self._my_statistics_model_type_selection = 'my_{}_statistics_model_type_selection'.format(self._tab)
        self._my_statistics_pattern_type_selection = 'my_{}_statistics_pattern_type_selection'.format(self._tab)
        self._my_statistics_chart_div = 'my_{}_statistics_chart_div'.format(self._tab)
        self._my_statistics = 'my_{}_statistics'.format(self._tab)

    def __fill_df_base__(self, pattern_type=''):
        self._df_base = self.__get_df_base__()
        if pattern_type != '':
            self._df_base = self._df_base[self._df_base[DC.PATTERN_TYPE] == pattern_type]
        self.__manipulate_ptc_columns__()

    def __get_df_base__(self) -> pd.DataFrame:
        return self.sys_config.db_stock.get_pattern_records_as_dataframe()

    def __init_dd_handler__(self):
        self._dd_handler = PatternStatisticsDropDownHandler()

    def __init_plotter__(self):
        self._plotter = MyDashTabStatisticsPlotter4Pattern(self._df_base, self._color_handler)

    def __manipulate_ptc_columns__(self):
        for column in self._df_base.columns:
            if column[-4:] == '_PCT':
                self._df_base[column] = self._df_base[column].apply(round)

    def init_callbacks(self):
        self.__init_callback_for_numbers__()
        self.__init_callback_for_pattern_type_label__()
        self.__init_callback_for_pattern_type_numbers__()
        self.__init_callbacks_for_drop_down_visibility__()
        self.__init_callbacks_for_chart__()
        self.__init_callback_for_markdown__()
        self.__init_callback_for_x_variable_options__()
        self.__init_callback_for_y_variable_options__()

    def __init_callback_for_numbers__(self):
        @self.app.callback(
            Output(self._my_statistics_div, 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_pattern_numbers(n_intervals: int):
            self.__fill_df_base__()
            return self.__get_numbers_for_callback__()

    def __get_numbers_for_callback__(self):
        number_all = self._df_base.shape[0]
        number_pos = self._df_base[self._df_base[self.column_result] == 1].shape[0]
        number_neg = self._df_base[self._df_base[self.column_result] != 1].shape[0]
        return '{} (+{}/-{})'.format(number_all, number_pos, number_neg)

    def __init_callback_for_pattern_type_label__(self):
        @self.app.callback(
            Output(self._my_statistics_detail_label_div, 'children'),
            [Input(self._my_statistics_pattern_type_selection, 'value')])
        def handle_callback_for_pattern_type_label(pattern_type: str):
            return '' if pattern_type == FT.ALL else '{}:'.format(pattern_type)

    def __init_callback_for_pattern_type_numbers__(self):
        @self.app.callback(
            Output(self._my_statistics_detail_div, 'children'),
            [Input(self._my_statistics_pattern_type_selection, 'value')])
        def handle_callback_for_pattern_pattern_type_numbers(pattern_type: str):
            if pattern_type == FT.ALL:
                return ''
            self.__fill_df_base__(pattern_type)
            return self.__get_numbers_for_callback__()

    def __init_callback_for_y_variable_options__(self):
        @self.app.callback(
            Output(self._my_statistics_y_variable_selection, 'options'),
            [Input(self._my_statistics_chart_type_selection, 'value'),
             Input(self._my_statistics_predictor_selection, 'value')]
        )
        def handle_callback_for_category_options(chart_type: str, predictor: str):
            value_list = self.__get_value_list_for_y_variable_options__(chart_type, predictor)
            return [{'label': value.replace('_', ' '), 'value': value} for value in value_list]

    def __init_callback_for_x_variable_options__(self):
        @self.app.callback(
            Output(self._my_statistics_x_variable_selection, 'options'),
            [Input(self._my_statistics_chart_type_selection, 'value'),
             Input(self._my_statistics_predictor_selection, 'value')]
        )
        def handle_callback_for_x_variable_options(chart_type: str, predictor: str):
            value_list = self.__get_value_list_for_x_variable_options__(chart_type, predictor)
            # print('handle_callback_for_x_variable_options ({}-{}): {}'.format(chart_type, predictor, value_list))
            return [{'label': value.replace('_', ' '), 'value': value} for value in value_list]

    @staticmethod
    def __get_value_list_for_x_variable_options__(chart_type: str, predictor: str):
        return []

    @staticmethod
    def __get_value_list_for_y_variable_options__(chart_type: str, predictor: str):
        return []

    def __init_callbacks_for_drop_down_visibility__(self):
        for drop_down_type in [DDT.PREDICTOR, DDT.CATEGORY, DDT.X_VARIABLE, DDT.Y_VARIABLE, DDT.CHART_TEXT_VARIABLE]:
            @self.app.callback(
                Output(self._dd_handler.get_embracing_div_id(drop_down_type), 'style'),
                [Input(self._dd_handler.get_element_id(DDT.CHART_TYPE), 'value')],
                [State(self._dd_handler.get_embracing_div_id(drop_down_type), 'id')])
            def handle_selection_callback(chart_type: str, div_id: str):
                dd_type = self._dd_handler.get_drop_down_type_by_embracing_div_id(div_id)
                style_show = self._dd_handler.get_style_display(dd_type)
                if dd_type == DDT.PREDICTOR:
                    if chart_type != CHT.PREDICTOR:
                        return {'display': 'none'}
                if dd_type == DDT.CATEGORY:
                    if chart_type == CHT.PREDICTOR:
                        return {'display': 'none'}
                elif chart_type == CHT.AREA_WINNER_LOSER:
                    if dd_type in [DDT.Y_VARIABLE, DDT.CHART_TEXT_VARIABLE]:
                        return {'display': 'none'}
                elif chart_type == CHT.PIE:
                    return {'display': 'none'}
                return style_show

    def __init_callbacks_for_chart__(self):
        @self.app.callback(
            Output(self._my_statistics_chart_div, 'children'),
            [Input(self._my_statistics_chart_type_selection, 'value'),
             Input(self._my_statistics_predictor_selection, 'value'),
             Input(self._my_statistics_category_selection, 'value'),
             Input(self._my_statistics_x_variable_selection, 'value'),
             Input(self._my_statistics_y_variable_selection, 'value'),
             Input(self._my_statistics_text_variable_selection, 'value'),
             Input(self._my_statistics_pattern_type_selection, 'value'),
             Input('my_interval_refresh', 'n_intervals')])
        def handle_interval_callback_with_date_picker(ct: str, predictor: str, category: str, x: str, y: str,
                                                      text_column: str, pt: str, n_intervals: int):
            self._plotter.predictor = predictor
            self._plotter.category = category
            self._plotter.chart_type = ct
            self._plotter.x_variable = x
            self._plotter.y_variable = y
            self._plotter.text_variable = text_column
            self._plotter.pattern_type = pt
            return self.__get_charts_from_plotter__()

        @self.app.callback(
            Output(self._my_statistics_chart_type_div, 'children'),
            [Input(self._my_statistics_chart_type_selection, 'value')])
        def handle_callback_for_chart_type_selection_for_chart_type(chart_type: str):
            return chart_type

    def __init_callback_for_markdown__(self):
        @self.app.callback(
            Output(self._my_statistics_markdown, 'children'),
            [Input(self._my_statistics_chart_type_selection, 'value')])
        def handle_callback_for_ticket_markdown(chart_type: str):
            text = dedent('''
                            **Last tick:** open:{} - **close = {}**

                            **Annotations (next breakout)**: {}
                            ''').format('open', 'close', chart_type)
            return text

