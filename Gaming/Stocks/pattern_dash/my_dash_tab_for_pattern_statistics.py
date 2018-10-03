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
from sertl_analytics.constants.pattern_constants import DC, CHT
from pattern_dash.my_dash_components import MyHTML
from pattern_dash.my_dash_header_tables import MyHTMLTabPatternStatisticsHeaderTable
from pattern_dash.my_dash_drop_down import DDT, PatternStatisticsDropDownHandler
from pattern_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter4Pattern
from textwrap import dedent


class MyDashTab4PatternStatistics(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyDashBaseTab.__init__(self, app, sys_config)
        self._df_base = self.sys_config.db_stock.get_pattern_records_as_dataframe()
        self._dd_handler = PatternStatisticsDropDownHandler()
        self._plotter = MyDashTabStatisticsPlotter4Pattern(self._df_base)

    def get_div_for_tab(self):
        children_list = [
            MyHTMLTabPatternStatisticsHeaderTable().get_table(),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TYPE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CATEGORY)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.X_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.Y_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.CHART_TEXT_VARIABLE)),
            MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(DDT.PATTERN_TYPE)),
            MyHTML.div('my_pattern_statistics_chart_div', self._plotter.get_chart(), False),
        ]
        return MyHTML.div('my_pattern_statistics', children_list)

    def init_callbacks(self):
        self.__init_callback_for_numbers__()
        self.__init_callbacks_for_drop_down_visibility__()
        self.__init_callbacks_for_chart__()
        self.__init_callback_for_markdown__()

    def __init_callback_for_numbers__(self):
        @self.app.callback(
            Output('my_pattern_statistics_div', 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_callback_for_numbers(n_intervals: int):
            number_all = self._df_base.shape[0]
            number_pos = self._df_base[self._df_base[DC.EXPECTED_WIN_REACHED] == 1].shape[0]
            number_neg = self._df_base[self._df_base[DC.EXPECTED_WIN_REACHED] == 0].shape[0]
            return '{} (+{}/-{})'.format(number_all, number_pos, number_neg)

    def __init_callbacks_for_drop_down_visibility__(self):
        for drop_down_type in [DDT.X_VARIABLE, DDT.Y_VARIABLE, DDT.CHART_TEXT_VARIABLE]:
            @self.app.callback(
                Output(self._dd_handler.get_embracing_div_id(drop_down_type), 'style'),
                [Input(self._dd_handler.get_element_id(DDT.CHART_TYPE), 'value')],
                [State(self._dd_handler.get_embracing_div_id(drop_down_type), 'id')])
            def handle_selection_callback(chart_type: str, div_id: str):
                dd_type = self._dd_handler.get_drop_down_type_by_embracing_div_id(div_id)
                style_show = self._dd_handler.get_style_display(dd_type)
                if chart_type == CHT.AREA_WINNER_LOSER:
                    if dd_type in [DDT.Y_VARIABLE, DDT.CHART_TEXT_VARIABLE]:
                        return {'display': 'none'}
                elif chart_type == CHT.PIE:
                    return {'display': 'none'}
                return style_show

    def __init_callbacks_for_chart__(self):
        @self.app.callback(
            Output('my_pattern_statistics_chart_div', 'children'),
            [Input('my_pattern_statistics_chart_type_selection', 'value'),
             Input('my_pattern_statistics_category_selection', 'value'),
             Input('my_pattern_statistics_x_variable_selection', 'value'),
             Input('my_pattern_statistics_y_variable_selection', 'value'),
             Input('my_pattern_statistics_text_variable_selection', 'value'),
             Input('my_pattern_statistics_pattern_type_selection', 'value')])
        def handle_interval_callback_with_date_picker(ct: str, category: str, x: str, y: str, text_column: str, pt: str):
            self._plotter.category = category
            self._plotter.chart_type = ct
            self._plotter.x_variable = x
            self._plotter.y_variable = y
            self._plotter.text_variable = text_column
            self._plotter.pattern_type = pt
            return self._plotter.get_chart()

        @self.app.callback(
            Output('my_pattern_statistics_chart_type_div', 'children'),
            [Input('my_pattern_statistics_chart_type_selection', 'value')])
        def handle_callback_for_chart_type_selection_for_chart_type(chart_type: str):
            return chart_type

    def __init_callback_for_markdown__(self):
        @self.app.callback(
            Output('my_pattern_statistics_markdown', 'children'),
            [Input('my_pattern_statistics_chart_type_selection', 'value')])
        def handle_callback_for_ticket_markdown(chart_type: str):
            text = dedent('''
                            **Last tick:** open:{} - **close = {}**

                            **Annotations (next breakout)**: {}
                            ''').format('open', 'close', chart_type)
            return text

