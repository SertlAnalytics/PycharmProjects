"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from sertl_analytics.constants.pattern_constants import TP
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import json
from pattern_detection_controller import PatternDetectionController
from pattern_database.stock_tables_data_dictionary import AssetDataDictionary
from sertl_analytics.constants.pattern_constants import BT, PRD, INDICES
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.my_text import MyText
from pattern_dash.my_dash_tools import MyGraphCache, MyDashStateHandler, MyGraphCacheObjectApi
from sertl_analytics.mydash.my_dash_components import MyDCC, MyHTML, DccGraphApi, DccGraphSecondApi
from pattern_dash.my_dash_tab_dd_for_pattern import PatternTabDropDownHandler, PDD
from pattern_dash.my_dash_header_tables import MyHTMLTabPatternHeaderTable
from pattern_trade_handler import PatternTradeHandler
from textwrap import dedent
from pattern_dash.my_dash_base_tab_for_pattern import MyPatternDashBaseTab, Dash
from pattern_dash.my_dash_configuration_tables import MyHTMLSystemConfigurationTable
from sertl_analytics.mydates import MyDate


class MyDashTab4Pattern(MyPatternDashBaseTab):
    def __init__(self, app: Dash, sys_config: SystemConfiguration, trade_handler_online: PatternTradeHandler):
        MyPatternDashBaseTab.__init__(self, app, sys_config)
        self.bitfinex_config = self.sys_config.exchange_config
        self.trade_handler_online = trade_handler_online
        self.sys_config_second = sys_config.get_semi_deep_copy()
        self.sys_config_fibonacci = self.sys_config.get_semi_deep_copy()
        self._pattern_controller = PatternDetectionController(self.sys_config, TP.ONLINE)
        self.detector = None
        self._index_options = self.sys_config.index_config.get_indices_as_options()
        self._ticker_options = []
        self._ticker_selected = ''
        self.__fill_ticker_options__()
        self._dd_handler = PatternTabDropDownHandler(self._index_options, self._ticker_options)
        self._time_stamp_next_refresh = None
        self._graph_first_data_provider_api = None
        self._graph_second_data_provider_api = None
        self._graph_first_cache = MyGraphCache('my_graph_first')
        self._graph_second_cache = MyGraphCache('my_graph_second')
        self._state_handler = MyDashStateHandler(self._ticker_options)
        self._graph_key_first = ''
        self._detector_first = None
        self._pattern_data_first = None
        self._balance_saving_times = MyDate.get_epoch_seconds_for_current_day_as_list()

    def init_callbacks(self):
        self.__init_interval_callback_for_interval_details__()
        self.__init_interval_setting_callback__()
        self.__init_callback_for_stock_symbol_options__()
        self.__init_callback_for_position_markdown__()
        self.__init_callback_for_dashboard_markdown__()
        self.__init_callback_for_pattern_markdown__()
        self.__init_callback_for_graph_first__()
        self.__init_callback_for_graph_second__()
        self.__init_callback_for_graphs_before_breakout__()
        self.__init_hover_over_callback__()
        self.__init_selection_callback__()
        self.__init_ticker_selection_callback__()
        # self.__init_callback_for_system_configuration_table__()

    def __init_callback_for_system_configuration_table__(self):
        @self.app.callback(
            Output('my_table_SystemConfiguration', 'children'),
            [Input('my_period_aggregation', 'value')])
        def handle_callback_for_system_configuration_table(aggregation: str):
            print('_aggregation = {}, children={}'.format(aggregation, ''))
            return MyHTMLSystemConfigurationTable(self.sys_config).get_table()

    def get_div_for_tab(self):
        # print('MyHTMLHeaderTable.get_table={}'.format(MyHTMLHeaderTable().get_table()))
        li = [MyHTMLTabPatternHeaderTable().get_table()]
        li.append(MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(PDD.INDEX))),
        li.append(MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(PDD.STOCK_SYMBOL)))
        li.append(MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(
            PDD.PERIOD_AGGREGATION, default_value=self.sys_config.period_aggregation)))
        li.append(MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(PDD.REFRESH_INTERVAL)))
        li.append(MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(PDD.SECOND_GRAPH_RANGE)))
        if self.sys_config.from_db:
            li.append(self.__get_html_div_with_date_picker_range__())
        li.append(MyHTML.div_with_html_button_submit('my_refresh_button', 'Refresh'))
        li.append(MyHTML.div('my_graph_first_div'))
        li.append(MyHTML.div('my_graph_second_div'))
        li.append(MyHTML.div('my_graphs_before_breakout_div'))
        # li.append(MyHTML.div_embedded('my_graphs_before_breakout_div'))
        li.append(MyHTML.div_with_html_pre('my_hover_data'))
        return MyHTML.div('', li)

    @staticmethod
    def __get_html_div_with_date_picker_range__():
        return html.Div(
            [
                MyHTML.h3('Select start and end dates:'),
                MyDCC.get_date_picker_range('my_date_picker', datetime.today() - timedelta(days=160))
            ],
            style={'display': 'inline-block', 'vertical-align': 'bottom', 'height': 20}
        )

    def __init_callback_for_position_markdown__(self):
        @self.app.callback(
            Output('my_position_markdown', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_callback_for_position_markdown(n_intervals: int):
            # self.__add_fibonacci_waves_to_news__()
            # self.__add_bollinger_band_breaks_to_news__()
            markdown_text = self.__get_position_markdown__(n_intervals)
            self.__save_balances_to_database__()  # this must be after __get_position_markdown__ !!!
            return markdown_text

    def __save_balances_to_database__(self):
        if len(self._balance_saving_times) == 0:  # already all done
            return
        processed_list = []
        ts_now = MyDate.get_epoch_seconds_from_datetime()
        for ts_saving in self._balance_saving_times:
            if ts_saving <= ts_now:
                dt_saving = MyDate.get_date_time_from_epoch_seconds_as_string(ts_saving)
                self.__save_balances__(ts_saving, dt_saving)
                processed_list.append(ts_saving)
        for values in processed_list:
            self._balance_saving_times.remove(values)

    def __save_balances__(self, ts_saving: int, dt_saving: str):
        if self.sys_config.db_stock.is_any_asset_already_available_for_timestamp(ts_saving):
            return
        for position in self.trade_handler_online.balances:
            data_dict = AssetDataDictionary().get_data_dict_for_target_table_for_balance(position, ts_saving, dt_saving)
            self.sys_config.db_stock.insert_asset_entry(data_dict)

    def __init_callback_for_dashboard_markdown__(self):
        @self.app.callback(
            Output('my_dashboard_markdown', 'children'),
            [Input('my_interval_timer', 'n_intervals')])
        def handle_callback_for_dashboard_markdown(n_intervals: int):
            return self.__get_dashboard_markdown__(n_intervals)

    def __get_dashboard_markdown__(self, n_intervals: int):
        news = self.__get_markdown_news__()
        trades = self.__get_markdown_trades__()
        statistics = self.__get_markdown_statistics__()
        text = '- _**News**_: {}\n- _**Trades**_: {}\n - _**Daily statistics**_: {}'.format(news, trades, statistics)
        return text

    def __get_position_markdown__(self, n_intervals: int):
        text = dedent('''{}''').format(self.__get_position_markdown_for_active_positions__())
        return text

    def __get_position_markdown_for_active_positions__(self):
        balances = self.trade_handler_online.get_balances_with_current_values()
        self.trade_handler_online.balances = balances
        text_list = ['_**{}**_: {:.2f} ({:.2f}): {:.2f}$'.format(
                b.asset, b.amount, b.amount_available, b.current_value) for b in balances]
        total_value = sum([balance.current_value for balance in balances])
        text_list.append(self.__get_position_total__(total_value))
        return '  \n'.join(text_list)

    def __get_position_total__(self, total_value: float):
        if self.trade_handler_online.value_total_start == 0:
            self.trade_handler_online.value_total_start = total_value
        diff_value = total_value - self.trade_handler_online.value_total_start
        diff_pct = diff_value/self.trade_handler_online.value_total_start*100
        return '_**Total**_: {:.2f}$ ({:+.2f}$ / {:+.2f}%)'.format(total_value, diff_value, diff_pct)

    def __get_markdown_news__(self):
        return self._news_handler.get_news_for_markdown_since_last_refresh(self._time_stamp_last_refresh)

    def __add_fibonacci_waves_to_news__(self):
        # example: Fibonacci: BTCUSD (15min): descending - last tick at 10:30:00
        sys_config = self.sys_config_fibonacci
        indicator_list = self.bitfinex_config.get_fibonacci_indicators()
        result_list = []
        # indicator_list = [['XMRUSD', 15]]
        for indicators in indicator_list:
            sys_config.init_by_indicator(indicators)
            detector = self._pattern_controller.get_detector_for_fibonacci(sys_config, indicators[0])
            for fib_wave in detector.fib_wave_tree.fibonacci_wave_list:
                aggregation = indicators[1]
                if fib_wave.is_wave_indicator_for_dash(aggregation):
                    result_list.append('{} ({}min): {}'.format(
                        indicators[0], aggregation, fib_wave.get_details_as_dash_indicator()))
            for fib_wave in detector.fib_wave_tree.get_actual_forecast_wave_list():
                aggregation = indicators[1]
                result_list.append('{} ({}min): {}'.format(
                    indicators[0], aggregation, fib_wave.get_details_as_dash_forecast_indicator()))
        if len(result_list) > 0:
            self.sys_config.sound_machine.play_alarm_fibonacci()
            self._news_handler.add_news('Fibonacci', ', '.join(result_list))

    def __add_bollinger_band_breaks_to_news__(self):
        # example: Bollinger break: BTCUSD (15min): last tick at 10:30:00
        sys_config = self.sys_config_fibonacci
        indicator_list = self.bitfinex_config.get_bollinger_band_indicators()
        result_list = []
        # indicator_list = [['XMRUSD', 15]]
        for indicators in indicator_list:
            sys_config.init_by_indicator(indicators)
            detector = self._pattern_controller.get_detector_for_bollinger_band(sys_config, indicators[0])
            bollinger_bound_break_direction = detector.pdh.get_bollinger_band_boundary_break_direction()
            if bollinger_bound_break_direction != '':
                aggregation = indicators[1]
                msg = '{} broken'.format(bollinger_bound_break_direction)
                result_list.append('{} ({}min): {}'.format(indicators[0], aggregation, msg))
        if len(result_list) > 0:
            self.sys_config.sound_machine.play_alarm_bollinger_band_break()
            self._news_handler.add_news('Bollinger Band', ', '.join(result_list))

    def __get_markdown_trades__(self):
        return '- none -'

    def __get_markdown_statistics__(self):
        return '- none -'

    def __init_interval_callback_for_interval_details__(self):
        @self.app.callback(
            Output('my_last_refresh_time_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals')])
        def handle_interval_callback_for_last_refresh(n_intervals):
            # self._news_handler.clear()
            self._time_stamp_last_refresh = MyDate.time_stamp_now()
            last_refresh_dt = MyDate.get_time_from_datetime(datetime.now())
            return '{} ({})'.format(last_refresh_dt, n_intervals)

        @self.app.callback(
            Output('my_next_refresh_time_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals'), Input('my_interval_refresh', 'interval')])
        def handle_interval_callback_for_next_refresh(n_intervals, interval_ms):
            dt_next = datetime.now() + timedelta(milliseconds=interval_ms)
            self._time_stamp_next_refresh = int(dt_next.timestamp())
            return '{}'.format(MyDate.get_time_from_datetime(dt_next))

    def __init_interval_setting_callback__(self):
        @self.app.callback(
            Output('my_interval_refresh', 'interval'),
            [Input('my_interval_selection', 'value')])
        def handle_interval_setting_callback(interval_selected):
            print('Refresh interval set to: {}'.format(interval_selected))
            return interval_selected * 1000

    def __init_callback_for_stock_symbol_options__(self):
        @self.app.callback(
            Output('my_pattern_ticker_selection', 'options'),
            [Input('my_pattern_index_selection', 'value')])
        def handle_callback_for_stock_symbol_options(selected_index: str):
            # print('__init_callback_for_stock_symbol_options__: selected_index={}'.format(selected_index))
            self.sys_config.data_provider.use_index(selected_index)
            self.__fill_ticker_options__()
            # print('__init_callback_for_stock_symbol_options__: options={}'.format(self._ticker_options))
            return self._ticker_options

    def __init_callback_for_pattern_markdown__(self):
        @self.app.callback(
            Output('my_pattern_markdown', 'children'),
            [Input('my_graph_first_div', 'children')])
        def handle_callback_for_ticket_markdown(children):
            annotation = self.__get_annotation_for_markdown__()
            wave_tick_list = self.trade_handler_online.get_latest_tickers_as_wave_tick_list(self._ticker_selected)
            text_list = [wave_tick_list.get_markdown_text_for_second_last_wave_tick(),
                         wave_tick_list.get_markdown_text_for_last_wave_tick()]
            if annotation != '':
                annotation = MyText.get_text_for_markdown(annotation)
                text_list.append('**Annotations (next breakout)**: {}'.format(annotation))
            return '  \n'.join(text_list)

    def __get_annotation_for_markdown__(self):
        annotation = ''
        for pattern in self._detector_first.pattern_list:
            if not pattern.was_breakout_done():
                annotation = pattern.get_annotation_parameter().text
        return annotation

    def __init_callback_for_graph_first__(self):
        @self.app.callback(
            Output('my_graph_first_div', 'children'),
            [Input('my_interval_refresh', 'n_intervals'),
             Input('my_refresh_button', 'n_clicks')],
            [State('my_pattern_ticker_selection', 'value')])
        def handle_callback_for_graph_first(n_intervals, n_clicks, ticker):
            self._ticker_selected = ticker
            graph, graph_key = self.__get_graph_first__(ticker)
            self._graph_key_first = graph_key
            self.__cache_others_ticker_values__(n_intervals, ticker)
            if self._graph_first_cache.was_breakout_since_last_data_update(graph_key):
                self._news_handler.add_news(ticker, 'Breakout since last data refresh !!!!')
                self.sys_config.sound_machine.play_alarm_new_pattern()
            elif self._graph_first_cache.was_touch_since_last_data_update(graph_key):
                self._news_handler.add_news(ticker, 'Touch since last data refresh !!!!')
                self.sys_config.sound_machine.play_alarm_touch_point()
            return graph

    def __cache_others_ticker_values__(self, n_intervals: int, ticker_selected: str):
        if n_intervals > 0:
            for element_dict in self._ticker_options:
                ticker = element_dict['value']
                if ticker != ticker_selected:
                    self.__add_cache_object_for_ticker_to_graph_first_cache__(ticker)

    def __init_callback_for_graph_second__(self):
        @self.app.callback(
            Output('my_graph_second_div', 'children'),
            [Input('my_graph_second_days_selection', 'value'),
             Input('my_graph_first_div', 'children')],
            [State('my_pattern_ticker_selection', 'value'),
             State('my_period_aggregation', 'value')])
        def handle_callback_for_graph_second(days_selected, graph_first_div, ticker_selected: str, aggregation: int):
            if days_selected == 0 or ticker_selected is None:
                return ''
            self.__set_period_aggregation_to_sys_configs__(aggregation)
            return self.__get_graph_second__(ticker_selected, days_selected)[0]

    def __init_callback_for_graphs_before_breakout__(self):
        @self.app.callback(
            Output('my_graphs_before_breakout_div', 'children'),
            [Input('my_graph_first_div', 'children')])
        def handle_callback_for_graphs_before_breakout(graph_first_div):
            play_sound = False
            graphs, new_observations = self._graph_first_cache.get_graph_list_for_observation(self._graph_key_first)
            if new_observations:
                play_sound = True
                self._news_handler.add_news('Observations', 'Some new since last refresh !!!!')
            pattern_list = self._graph_first_cache.get_pattern_list_for_buy_trigger(BT.BREAKOUT)
            self.trade_handler_online.add_pattern_list_for_trade(pattern_list)
            if self._graph_first_cache.number_of_finished_fibonacci_waves_since_last_refresh > 2:
                self._news_handler.add_news('Fibonacci numbers', 'More than 2 waves finished since last refresh !!!!')
                play_sound = True
            if play_sound:
                self.sys_config.sound_machine.play_alarm_new_pattern()
            return graphs

    def __init_selection_callback__(self):
        @self.app.callback(
            Output('my_refresh_button', 'hidden'),
            [Input('my_pattern_ticker_selection', 'value'),
             Input('my_period_aggregation', 'value'),
             Input('my_interval_selection', 'value'),
             Input('my_interval_refresh', 'n_intervals'),
             Input('my_refresh_button', 'n_clicks')],
            [State('my_interval_timer', 'n_intervals'),
             State('my_pattern_index_selection', 'value')])
        def handle_selection_callback(ticker_selected, period_aggregation: int, interval_selected: int,
                                      n_intervals, n_clicks, n_intervals_sec, selected_indices: list):
            # print('selected_indizes: {}'.format(selected_indices))
            self.__set_period_aggregation_to_sys_configs__(period_aggregation)
            indices_change = self._state_handler.change_for_my_selected_indices(selected_indices)
            if indices_change:
                return ''
            pa_change = self._state_handler.change_for_my_period_aggregation_selection(period_aggregation)
            i_change = self._state_handler.change_for_my_interval_selection(interval_selected)
            if pa_change or i_change:
                self._graph_first_cache.clear()
            if self._state_handler.change_for_my_interval(n_intervals):  # hide button after interval refresh
                return 'hidden'
            if self._state_handler.change_for_my_refresh_button(n_clicks):  # hide button after refresh button click
                return 'hidden'
            return 'hidden' if n_intervals_sec == 0 else ''

        @self.app.callback(
            Output('my_ticker_div', 'children'),
            [Input('my_pattern_ticker_selection', 'value')])
        def handle_ticker_selection_callback_for_ticker_label(ticker_selected):
            return self.__get_ticker_label__(ticker_selected)

    def __set_period_aggregation_to_sys_configs__(self, selected_period_aggregation: int):
        self.sys_config.data_provider.aggregation = selected_period_aggregation
        self.sys_config_second.data_provider.aggregation = self.__get_period_aggregation_for_second_graph__()

    def __get_period_aggregation_for_second_graph__(self):
        return {5: 15, 15: 30, 30: 15}.get(self.sys_config.period_aggregation)

    def __init_hover_over_callback__(self):
        @self.app.callback(
            Output('my_hover_data', 'children'),
            [Input('my_graph_first', 'hoverData'), Input('my_graph_second', 'hoverData')])
        def handle_hover_over_callback(hover_data_graph_1, hover_data_graph_2):
            return json.dumps(hover_data_graph_1, indent=2) + '\n' + json.dumps(hover_data_graph_2, indent=2)

    def __init_ticker_selection_callback__(self):
        @self.app.callback(
            Output('my_graph_second_days_selection', 'value'),
            [Input('my_pattern_ticker_selection', 'value')],
            [State('my_graph_second_days_selection', 'value')])
        def handle_ticker_selection_callback_for_days_selection(ticker_selected, second_days_selection):
            return second_days_selection if second_days_selection == 1 else 0  # we want to keep Intraday

    def __get_graph_first__(self, ticker: str, and_clause=''):
        self.__add_cache_object_for_ticker_to_graph_first_cache__(ticker, and_clause)
        graph_key = self._graph_first_cache.get_cache_key(ticker, 0)
        cached_graph = self._graph_first_cache.get_cached_object_by_key(graph_key)
        self._detector_first = self._graph_first_cache.get_detector(graph_key)
        self._pattern_data_first = self._graph_first_cache.get_pattern_data(graph_key)
        return cached_graph, graph_key

    def __add_cache_object_for_ticker_to_graph_first_cache__(self, ticker: str, and_clause=''):
        graph_id = self._graph_first_cache.graph_id
        cache_key = self._graph_first_cache.get_cache_key(ticker, 0)
        if self._graph_first_cache.get_cached_object_by_key(cache_key) is None:
            aggregation = self.sys_config.period_aggregation
            graph_title = self.__get_graph_title__(ticker, self.sys_config.period, aggregation)
            detector = self._pattern_controller.get_detector_for_dash(self.sys_config, ticker, and_clause)
            pattern_data = detector.pdh.pattern_data
            graph_api = DccGraphApi(graph_id, graph_title)
            graph_api.ticker_id = ticker
            graph_api.df = detector.pdh.pattern_data.df
            graph = self.__get_dcc_graph_element__(detector, graph_api)
            cache_api = self.__get_cache_api__(cache_key, graph, detector, pattern_data)
            self._graph_first_cache.add_cache_object(cache_api)
            print('{}: Cached into graph_first_cache: {}'.format(MyDate.get_time_str_from_datetime(), cache_key))
        else:
            print('{}: Already cached by graph_first_cache: {}'.format(MyDate.get_time_str_from_datetime(), cache_key))

    @staticmethod
    def __get_graph_title__(ticker, period: str, aggregation: int, days: int=0):
        if period == PRD.DAILY:
            return '{} {} ({}days)'.format(ticker, period, days)
        return '{} {} ({}min)'.format(ticker, period, aggregation)

    def __get_graph_second__(self, ticker: str, days: int):
        graph_id = self._graph_second_cache.graph_id
        period = PRD.DAILY if days > 1 else PRD.INTRADAY
        aggregation_second_graph = self.__get_period_aggregation_for_second_graph__()
        graph_title = self.__get_graph_title__(ticker, period, aggregation_second_graph, days)
        graph_key = self._graph_second_cache.get_cache_key(ticker, days, aggregation_second_graph)
        cached_graph = self._graph_second_cache.get_cached_object_by_key(graph_key)
        if cached_graph is not None:
            # print('...return cached graph_second: {}'.format(graph_key))
            return cached_graph, graph_key
        self.__update_data_provider_parameters_for_graph_second__(days, period, aggregation_second_graph)
        if days == 1:
            detector = self._pattern_controller.get_detector_for_dash(self.sys_config_second, ticker)
            graph_api = DccGraphSecondApi(graph_id, graph_title)
            graph_api.ticker_id = ticker
            graph_api.df = detector.pdh.pattern_data.df
            graph = self.__get_dcc_graph_element__(detector, graph_api)
            cache_api = self.__get_cache_api__(graph_key, graph, detector, None)
            self._graph_second_cache.add_cache_object(cache_api)
        else:
            date_from = datetime.today() - timedelta(days=days)
            date_to = datetime.today() + timedelta(days=5)
            and_clause = self.sys_config.data_provider.get_and_clause(date_from, date_to)
            detector = self._pattern_controller.get_detector_for_dash(self.sys_config_second, ticker, and_clause)
            graph_api = DccGraphSecondApi(graph_id, graph_title)
            graph_api.ticker_id = ticker
            graph_api.df = detector.pdh.pattern_data.df
            graph = self.__get_dcc_graph_element__(detector, graph_api)
            cache_api = self.__get_cache_api__(graph_key, graph, detector, None)
            self._graph_second_cache.add_cache_object(cache_api)
        return graph, graph_key

    def __update_data_provider_parameters_for_graph_second__(self, days: int, period: str, aggregation: int=1):
        if days == 1:
            self.sys_config_second.data_provider.from_db = False
            self.sys_config_second.data_provider.period = period
            self.sys_config_second.data_provider.aggregation = aggregation
        else:
            self.sys_config_second.data_provider.from_db = True
            self.sys_config_second.data_provider.period = period
            self.sys_config_second.data_provider.aggregation = 1

    def __get_cache_api__(self, graph_key, graph, detector, pattern_data):
        cache_api = MyGraphCacheObjectApi(self.sys_config)
        cache_api.key = graph_key
        cache_api.object = graph
        cache_api.detector = detector
        cache_api.pattern_data = pattern_data
        cache_api.valid_until_ts = self._time_stamp_next_refresh
        cache_api.last_refresh_ts = self._time_stamp_last_refresh
        return cache_api

    def __fill_ticker_options__(self):
        self._ticker_options = []
        if self.sys_config.data_provider.index_used == INDICES.CRYPTO_CCY:
            for ticker_id in self.bitfinex_config.ticker_id_list:
                if ticker_id in self.sys_config.data_provider.ticker_dict:
                    name = self.sys_config.data_provider.ticker_dict[ticker_id]
                    self._ticker_options.append({'label': '{}'.format(name), 'value': ticker_id})
        else:  # currently we take all - but this is definitely to much for calculation...
            for symbol, name in self.sys_config.data_provider.ticker_dict.items():
                self._ticker_options.append({'label': '{}'.format(name), 'value': symbol})

    def __get_ticker_label__(self, ticker_value: str):
        for elements in self._ticker_options:
            if elements['value'] == ticker_value:
                return elements['label']
        return ticker_value

