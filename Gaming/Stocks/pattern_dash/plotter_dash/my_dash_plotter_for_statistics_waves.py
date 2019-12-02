"""
Description: This module contains the plotter functions for waves statistics tabs.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from sertl_analytics.constants.pattern_constants import DC, CHT, WAVEST, PRD, FD
from sertl_analytics.constants.pattern_constants import INDICES
from sertl_analytics.mydates import MyDate
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from pattern_dash.my_dash_colors import DashColorHandler
from fibonacci.fibonacci_wave_data import FibonacciWaveDataHandler
import numpy as np
from pattern_dash.plotter_dash.my_dash_plotter_for_statistics import MyDashTabStatisticsPlotter


class MyDashTabStatisticsPlotter4Waves(MyDashTabStatisticsPlotter):
    def __init__(self, wave_handler: FibonacciWaveDataHandler, color_handler: DashColorHandler, index=''):
        self._wave_handler = wave_handler
        self._index = index
        MyDashTabStatisticsPlotter.__init__(self, self._wave_handler.df_wave, color_handler)

    def __init_parameter__(self):
        self.__init_parameter_by_chart_type__(CHT.HEAT_MAP)
        self._chart_id = 'waves_heatmap'
        self._chart_name = 'Waves'
        self.chart_type = CHT.HEAT_MAP

    def __init_parameter_by_chart_type__(self, chart_type: str):
        self.chart_type = chart_type
        if self.chart_type == CHT.HEAT_MAP:
            self._chart_id = 'waves_heatmap'
            self._chart_name = 'Waves'
        elif self.chart_type == CHT.MOOD_CHART:
            self._chart_id = 'waves_mood_chart'
            self._chart_name = 'Mood Chart'

    def __print_df_base__(self):
        columns = [DC.EQUITY_TYPE, DC.PERIOD, DC.WAVE_TYPE, DC.WAVE_END_DT]
        df_reduced = self._df_base[columns]
        print('__print_df_base__: _df_wave\n{}'.format(df_reduced.head(100)))

    def __get_chart_type_heatmap__(self):
        graph_list = []
        if self._index in ['', INDICES.ALL]:
            index_list = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
            # ToDo Add INDICES.DAX when we have intraday
        else:
            index_list = [self._index]
        for index in index_list:
            index_for_key = index.replace(' ', '_').lower()
            index_for_key = index_for_key if self._index == '' else '{}_{}'.format(index_for_key, 'single')
            chart_id = '{}_{}'.format(self._chart_id, index_for_key)
            # print('__get_chart_type_heatmap__: chart_id={}'.format(chart_id))
            chart_name = index
            graph_api = DccGraphApi(chart_id, chart_name)
            graph_api.figure_data = self.__get_heatmap_figure_data__(index)
            graph_api.figure_layout_height = 200
            graph_api.figure_layout_margin = {'b': 50, 'r': 50, 'l': 50, 't': 50}
            graph_list.append(MyDCC.graph(graph_api))
        return graph_list

    def __get_data_for_heatmap_figure__(self, index: str, for_mood_graph=False):
        x_data = self._wave_handler.tick_key_list_for_retrospection
        if self._wave_handler.period_for_retrospection == PRD.INTRADAY:
            x_data = [str(MyDate.get_date_time_from_epoch_seconds(key)) for key in x_data]
        y_data = WAVEST.get_waves_types_for_processing([self._wave_handler.period_for_retrospection])
        y_data = y_data[::-1]  # we want them in this order
        z_data = [self._wave_handler.get_waves_number_list_for_wave_type_and_index(wt, index) for wt in y_data]
        # print('__get_data_for_heatmap_figure__: {}: \n{}\n{}\n{}'.format(index, x_data, y_data, z_data))
        if for_mood_graph:
            return self.__get_heatmap_data_for_mood_graph__(x_data, y_data, z_data)
        return [x_data, y_data, z_data]

    @staticmethod
    def __get_heatmap_data_for_mood_graph__(x_data: list, y_data: list, z_data: list):
        """
        :param x_data=['2018-12-11', '2018-12-12', '2018-12-13', '2018-12-14',
        :param y_data=['intraday_descending', 'daily_descending', 'intraday_ascending', 'daily_ascending']
        :param z_data=[[2, 0, 1, 13, 4, 0, 0, 0, 0, 0, 1, 0, 0,...], [...], [...], [...]]
        :return:
        """
        z_data_dict = {wave_type: z_data[ind] for ind, wave_type in enumerate(y_data)}
        y_data_dict = {FD.ASC: list(np.add(z_data_dict[WAVEST.DAILY_ASC], z_data_dict[WAVEST.INTRADAY_ASC])),
                       FD.DESC: list(np.add(z_data_dict[WAVEST.DAILY_DESC], z_data_dict[WAVEST.INTRADAY_DESC])),
                       WAVEST.DAILY_ASC: z_data_dict[WAVEST.DAILY_ASC],
                       WAVEST.DAILY_DESC: z_data_dict[WAVEST.DAILY_DESC],
                       }
        return [x_data, y_data_dict]

    def __get_chart_type_mood__(self):
        graph_list = []
        if self._index in ['', INDICES.ALL]:
            index_list = [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100]
<<<<<<< HEAD
            # ToDo INDICES.Q_FSE
=======
            # ToDo Add INDICES.DAX when we have intraday
>>>>>>> c77ef10532f4aba0a02e95161d215a80963f9523
        else:
            index_list = [self._index]
        for index in index_list:
            index_for_key = index.replace(' ', '_').lower()
            index_for_key = index_for_key if self._index == '' else '{}_{}'.format(index_for_key, 'single')
            chart_id = '{}_{}'.format(self._chart_id, index_for_key)
            # print('__get_chart_type_heatmap__: chart_id={}'.format(chart_id))
            chart_name = index
            graph_api = DccGraphApi(chart_id, chart_name)
            figure_data, max_value = self.__get_mood_chart_figure_data__(index)
            max_value = int(round(max_value + 5, -1))
            value_interval = max(10, int(round(max_value/3, -1)))
            tick_vals = list(range(-max_value, max_value, value_interval))
            tick_text = [abs(value) for value in tick_vals]
            graph_api.figure_data = figure_data
            graph_api.figure_layout_height = 300
            graph_api.figure_layout_margin = {'b': 50, 'r': 50, 'l': 50, 't': 50}
            graph_api.figure_layout_barmode = 'overlay'
            graph_api.figure_layout_bargap = 0.1
            graph_api.figure_layout_x_axis_dict = {}
            graph_api.figure_layout_y_axis_dict = {'range': 'Date',
                                                   'tickvals': tick_vals,
                                                   'ticktext': tick_text}
            graph_list.append(MyDCC.graph(graph_api))
        return graph_list
