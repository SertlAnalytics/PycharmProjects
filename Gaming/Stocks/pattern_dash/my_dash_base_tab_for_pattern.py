"""
Description: This module is the base class for our dash - deferred classes required.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

import colorlover as cl
from dash import Dash
import pandas as pd
from sertl_analytics.mydash.my_dash_base_tab import MyDashBaseTab
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydash.my_dash_components import MyDCC, DccGraphApi
from sertl_analytics.constants.pattern_constants import CN, PRD, FD, INDI, INDICES, WAVEST
from sertl_analytics.mydates import MyDate
from pattern_detector import PatternDetector
from pattern_dash.my_dash_interface_for_pattern import DashInterface
from pattern_colors import PatternColorHandler
from pattern_trade import PatternTrade
from pattern_news_handler import NewsHandler
from pattern_wave_tick import WaveTickList, WaveTick


class MyPatternDashBaseTab(MyDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration):
        MyDashBaseTab.__init__(self, app)
        self.sys_config = sys_config
        self._news_handler = self.__get_news_handler__()
        self._fibonacci_wave_data_handler = sys_config.fibonacci_wave_data_handler

    def init_callbacks(self):
        pass

    def get_div_for_tab(self):
        pass

    def __get_color_handler__(self):
        return PatternColorHandler()

    @staticmethod
    def __get_news_handler__():
        delimiter = '  \n  - '  # news are a list in markdown
        return NewsHandler(delimiter, '- no news -')

    def __get_dcc_graph_element__(self, detector, graph_api: DccGraphApi):
        pattern_df = graph_api.df
        pattern_list = detector.pattern_list if detector else [graph_api.pattern_trade.pattern]
        # print('Pattern_list={}'.format(pattern_list))
        period = detector.sys_config.period if detector else graph_api.period
        # print('_period={} from detector:{}'.format(_period, detector is None))
        candlestick = self.__get_candlesticks_trace__(pattern_df, graph_api.ticker_id, period)
        # print(candlestick)
        shapes = self.__get_pattern_shape_list__(pattern_list)
        shapes += self.__get_pattern_regression_shape_list__(pattern_list)
        if detector:
            shapes += self.__get_fibonacci_shape_list__(detector)
            shapes += self.__get_wave_peak_shape_list__(detector)
        if graph_api.pattern_trade:
            # graph_api.pattern_trade.ticker_actual.print_ticker('__get_pattern_trade_shape_list__...: last ticker')
            shapes += self.__get_pattern_trade_shape_list__(graph_api.pattern_trade)
        if (graph_api.indicator == INDI.BOLLINGER or True) and detector is not None:
            indicator_shape_list = self.__get_indicator_shape_list__(detector, graph_api.indicator)
            shapes += indicator_shape_list
        graph_api.figure_layout_shapes = [my_shapes.shape_parameters for my_shapes in shapes]
        # print(' graph_api.figure_layout_shapes: {}'.format( graph_api.figure_layout_shapes))
        graph_api.figure_layout_annotations = [my_shapes.annotation_parameters for my_shapes in shapes]
        graph_api.figure_data = [candlestick]
        return MyDCC.graph(graph_api)

    def __get_pattern_shape_list__(self, pattern_list: list):
        return_list = []
        for pattern in pattern_list:
            colors = self._color_handler.get_colors_for_pattern(pattern)
            return_list.append(DashInterface.get_pattern_part_entry_shape(pattern, colors[0]))
            if pattern.was_breakout_done() and pattern.is_part_trade_available():
                return_list.append(DashInterface.get_pattern_part_trade_shape(pattern, colors[1]))
            if pattern.is_fibonacci:
                return_list.append(DashInterface.get_forecast_shape(pattern, colors[2]))
            # for shapes in return_list:
            #     print('x={}, \ny={}'.format(shapes.x, shapes.y))
        return return_list

    def __get_pattern_trade_shape_list__(self, pattern_trade: PatternTrade):
        return_list = []
        colors = self._color_handler.get_colors_for_pattern_trade(pattern_trade)
        shape_watching = DashInterface.get_pattern_trade_watching_shape(pattern_trade, colors[0])
        shape_buying = DashInterface.get_pattern_trade_buying_shape(pattern_trade, colors[1])
        shape_selling = DashInterface.get_pattern_trade_selling_shape(pattern_trade, colors[2])
        shape_after_selling = DashInterface.get_pattern_trade_after_selling_shape(pattern_trade, colors[3])
        if shape_watching:
            return_list.append(shape_watching)
        if shape_buying:
            return_list.append(shape_buying)
        if shape_selling:
            return_list.append(shape_selling)
        if shape_after_selling:
            return_list.append(shape_after_selling)
        return return_list

    @staticmethod
    def __get_pattern_regression_shape_list__(pattern_list: list):
        return_list = []
        for pattern in pattern_list:
            return_list.append(DashInterface.get_f_regression_shape(pattern.part_entry, 'skyblue'))
        return return_list

    @staticmethod
    def __get_fibonacci_shape_list__(detector: PatternDetector):
        return_list = []
        for fib_waves in detector.fib_wave_tree.fibonacci_wave_list:
            color = 'green' if fib_waves.wave_type == FD.ASC else 'red'
            return_list.append(DashInterface.get_fibonacci_wave_shape(detector.sys_config, fib_waves, color))
            # print('Fibonacci: {}'.format(return_list[-1].shape_parameters))
        return return_list

    def __get_wave_peak_shape_list__(self, detector: PatternDetector):
        return_list = []
        symbol = detector.sys_config.runtime_config.actual_ticker
        index = detector.sys_config.index_config.get_index_for_symbol(symbol)
        period = detector.sys_config.period
        # print('__get_wave_peak_shape_list__: symbol={}, index={}'.format(symbol, index))
        wave_tick_list = WaveTickList(detector.pdh.pattern_data.df)
        self._fibonacci_wave_data_handler.fill_wave_type_number_dict_for_ticks_in_wave_tick_list(
            wave_tick_list, index, period)
        for tick in wave_tick_list.tick_list:
            for wave_type in WAVEST.get_waves_types_for_processing([PRD.DAILY]):
                number_waves = tick.get_wave_number_for_wave_type(wave_type)
                if number_waves >= 1:  # in the pre-process we have already used thresholds
                    color = self._fibonacci_wave_data_handler.get_color_for_wave_type_and_period(wave_type, period)
                    shape = DashInterface.get_wave_peak_shape(
                        detector.sys_config, wave_tick_list, tick, wave_type, color)
                    if shape is not None:
                        return_list.append(shape)
        return return_list

    @staticmethod
    def __get_indicator_shape_list__(detector: PatternDetector, indicator: str):
        return_list = DashInterface.get_indicator_wave_shape_list(detector, indicator, 'deeppink')
        return return_list

    def __get_candlesticks_trace__(self, df: pd.DataFrame, ticker: str, period: str):
        # print(_df.head())
        if period == PRD.INTRADAY:
            x_value = df[CN.DATETIME]
            # print('{}: __get_candlesticks_trace__: x_value={}'.format(ticker, x_value))
        else:
            x_value = df[CN.DATE]
        # columns = [CN.TIMESTAMP, CN.DATE_RANGE, CN.TIME, CN.HIGH, CN.LOW, CN.DATETIME]
        # print('__get_candlesticks_trace__: _period={}, ticker={}, head={}, x_value={}'.format(
        #     _period, ticker, _df[columns].head(-5), x_value))
        candlestick = {
            'x': x_value,
            'open': df[CN.OPEN],
            'high': df[CN.HIGH],
            'low': df[CN.LOW],
            'close': df[CN.CLOSE],
            'type': 'candlestick',
            'name': ticker,
            'legendgroup': ticker,
            'hoverover': 'skip',
            'increasing': {'line': {'color': 'g'}},
            'decreasing': {'line': {'color': 'r'}}
        }
        return candlestick

    def __get_bollinger_band_trace__(self, df: pd.DataFrame, ticker: str, period: str):
        color_scale = cl.scales['9']['qual']['Paired']
        bb_bands = self.__get_bollinger_band_values__(df[CN.CLOSE])
        bollinger_traces = [{
            'x': df[CN.TIME] if period == PRD.INTRADAY else df[CN.DATE],
            'y': y,
            'type': 'scatter', 'mode': 'lines',
            'line': {'width': 1, 'color': color_scale[(i * 2) % len(color_scale)]},
            'hoverinfo': 'none',
            'legendgroup': ticker + ' - Bollinger',
            'showlegend': True if i == 0 else False,
            'name': '{} - bollinger bands'.format(ticker)
        } for i, y in enumerate(bb_bands)]
        return bollinger_traces

    @staticmethod
    def __get_bollinger_band_values__(price_df: pd.DataFrame, window_size=10, num_of_std=5):
        rolling_mean = price_df.rolling(window=window_size).mean()
        rolling_std = price_df.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return [rolling_mean, upper_band, lower_band]

