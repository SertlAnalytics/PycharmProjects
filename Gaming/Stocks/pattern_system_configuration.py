"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import INDICES, EQUITY_TYPE, PRD, PDP, CN, BT, TSTR, FT, OPS
from sertl_analytics.mydates import MyDate
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from sertl_analytics.my_http import MyHttpClient
from sertl_analytics.exchanges.interactive_broker import IBKRConfiguration
from pattern_configuration import PatternConfiguration
from pattern_runtime_configuration import RuntimeConfiguration
from pattern_debugger import PatternDebugger
from pattern_logging.pattern_log import PatternLog
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable, WaveTable, AssetTable
from pattern_id import PatternID
from pattern_predictor import PatternMasterPredictorHandler, PatternPredictorApi
from pattern_predictor_optimizer import PatternPredictorOptimizer
from pattern_data_provider import PatternDataProvider
from pattern_trade_optimizer import TradeOptimizer
from pattern_process_manager import PatternProcessManager
from copy import deepcopy
from pattern_sound.pattern_sound_machine import PatternSoundMachine
from pattern_dash.my_dash_caches import MyGraphCache, MyDataFrameCache
from pattern_index_configuration import IndexConfiguration
from fibonacci.fibonacci_predictor import FibonacciPredictor
from fibonacci.fibonacci_wave_data import FibonacciWaveDataHandler
from pattern_trade_models.trade_small_profit import TradeSmallProfit


class SystemConfiguration:
    is_http_connection_ok = MyHttpClient.do_we_have_internet_connection()  # class variable

    def __init__(self, for_semi_deep_copy=False, with_predictor=True, run_on_server=False):
        # print('SystemConfiguration.__init__: for_semi_deep_copy={}'.format(for_semi_deep_copy))
        self.run_on_server=run_on_server
        self.file_log = PatternLog()
        self.runtime_config = RuntimeConfiguration()
        self.crypto_config = BitfinexConfiguration()
        self.exchange_config = self.crypto_config
        self.exchange_config.small_profit_parameter_dict = self.__get_small_profit_parameter_dict__()
        self.shares_config = IBKRConfiguration()
        self.sound_machine = PatternSoundMachine()
        self.process_manager = PatternProcessManager()
        if for_semi_deep_copy:
            return
        self.config = PatternConfiguration()
        self.db_stock = StockDatabase()
        self.index_config = IndexConfiguration(self.db_stock, INDICES.get_index_list_for_index_configuration())
        self.pattern_table = PatternTable()
        self.trade_table = TradeTable()
        self.wave_table = WaveTable()
        self.asset_table = AssetTable()
        self.df_cache = MyDataFrameCache()
        self.graph_cache = MyGraphCache()
        self.data_provider = PatternDataProvider(self.config, self.index_config,
                                                 self.db_stock, self.df_cache, self.run_on_server)
        if with_predictor:
            self.predictor_optimizer = PatternPredictorOptimizer(self.db_stock)
            self.fibonacci_predictor = FibonacciPredictor(self.db_stock, 7)
            self.fibonacci_wave_data_handler = FibonacciWaveDataHandler(self.db_stock)
            self.master_predictor_handler = PatternMasterPredictorHandler(self.__get_pattern_predictor_api__(self.config))
            self.trade_strategy_optimizer = TradeOptimizer(self.db_stock, self.expected_win_pct)

    def __get_pattern_predictor_api__(self, config: PatternConfiguration):
        api = PatternPredictorApi(config, self.db_stock, self.pattern_table, self.trade_table)
        api.predictor_optimizer = self.predictor_optimizer
        return api

    def __get_small_profit_parameter_dict__(self):
        return TradeSmallProfit().get_small_profit_parameter_dict(
            self.exchange_config.small_profit_distance_from_mean_pct)

    @property
    def pdh(self):
        return self.data_provider.pdh

    @property
    def ticker_dict(self) -> dict:
        if self.data_provider.index_used != INDICES.CRYPTO_CCY:
            return self.data_provider.ticker_dict
        return_dict = {}
        main_ticker_dict = self.data_provider.ticker_dict
        for ticker_id in self.exchange_config.ticker_id_list:
            if ticker_id in main_ticker_dict:
                return_dict[ticker_id] = main_ticker_dict[ticker_id]
        return return_dict

    @property
    def from_db(self) -> bool:
        return self.data_provider.from_db

    @property
    def period(self) -> str:
        return self.data_provider.period

    @property
    def period_aggregation(self) -> int:
        return self.data_provider.aggregation

    @staticmethod
    def deactivate_pattern_log_and_pattern_database():
        PatternLog.log_activated = False
        StockDatabase.database_activated = False

    def init_detection_process_for_automated_trade_update(self, mean: int, sma_number: int):
        self.config.detection_process = PDP.UPDATE_TRADE_DATA
        self.config.pattern_type_list = FT.get_long_trade_able_types()
        self.exchange_config.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.LIMIT_FIX,
                                                                  TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP]}
        self.exchange_config.default_trade_strategy_dict = {BT.BREAKOUT: TSTR.LIMIT}
        self.config.detection_process = PDP.UPDATE_TRADE_DATA
        self.config.plot_data = False
        self.config.with_trading = True
        self.config.trading_last_price_mean_aggregation = mean
        self.config.simple_moving_average_number = sma_number  # default = 8
        self.config.save_pattern_data = False
        self.config.save_trade_data = True
        self.config.replace_existing_trade_data_on_db = False  # default = False
        self.config.plot_only_pattern_with_fibonacci_waves = False
        self.config.plot_min_max = True
        self.config.plot_volume = False
        self.config.length_for_local_min_max = 2
        self.config.length_for_local_min_max_fibonacci = 1
        self.config.bound_upper_value = CN.CLOSE
        self.config.bound_lower_value = CN.CLOSE
        self.config.fibonacci_tolerance_pct = 0.1  # default is 0.20
        self.sound_machine.is_active = False

    def init_detection_process_for_automated_pattern_update(self):
        date_now = MyDate.get_date_from_datetime()
        date_from = MyDate.adjust_by_days(date_now, -180)
        self.data_provider.and_clause = "Date BETWEEN '{}' AND '{}'".format(str(date_from), str(date_now))
        self.data_provider.from_db = True
        self.data_provider.period = PRD.DAILY
        self.config.pattern_type_list = FT.get_all()
        self.config.detection_process = PDP.UPDATE_PATTERN_DATA
        self.config.plot_data = False
        self.config.with_trading = False
        self.config.save_pattern_data = True
        self.config.save_trade_data = False
        self.config.save_wave_data = False
        self.config.plot_only_pattern_with_fibonacci_waves = False
        self.config.plot_min_max = False
        self.config.plot_volume = False
        self.config.length_for_local_min_max = 2
        self.config.length_for_local_min_max_fibonacci = 1
        self.config.bound_upper_value = CN.CLOSE
        self.config.bound_lower_value = CN.CLOSE

    def get_value_categorizer_tolerance_pct(self):
        return 0 if self.pdh is None else self.pdh.tolerance_pct

    def get_value_categorizer_tolerance_pct_buying(self):
        return 0 if self.pdh is None else self.pdh.tolerance_pct_buying

    def get_value_categorizer_tolerance_pct_equal(self):
        return 0 if self.pdh is None else self.pdh.tolerance_pct_equal

    @property
    def expected_win_pct(self):
        if self.data_provider.equity_type == EQUITY_TYPE.CRYPTO:
            return 0.8
        else:
            return 0.8 if self.period == PRD.INTRADAY else 0.8

    @property
    def master_predictor_touch_points(self):
        return self.master_predictor_handler.master_predictor_touch_points

    @property
    def master_predictor_before_breakout(self):
        return self.master_predictor_handler.master_predictor_before_breakout

    @property
    def master_predictor_after_breakout(self):
        return self.master_predictor_handler.master_predictor_after_breakout

    @property
    def master_predictor_for_trades(self):
        return self.master_predictor_handler.master_predictor_for_trades

    def init_predictors_without_condition_list(self):
        # to avoid that the current case is already within the training data... - for back testing...
        ticker_id = self.data_provider.ticker_id
        ac_pattern = self.data_provider.and_clause_for_pattern
        ac_trades = self.data_provider.and_clause_for_trade
        # print('init_predictors_without_condition_list: self.data_provider.and_clause={}'.format(self.data_provider.and_clause))
        # print('init_predictors_without_condition_list: ac_pattern={}'.format(ac_pattern))
        self.master_predictor_handler.init_predictors_without_condition_list(ticker_id, ac_pattern, ac_trades)

    def get_extended_pdh(self, ticker_id: str, limit: int):
        """
        This method is used to get the data from the source after certain online processes - like breakout, sell, ...
        :param ticker_id:
        :param and_clause:
        :param limit: The limit value was adjusted to the current tick with respect to the beginning limit
        :return: adjusted self.data_provider.pdh (=self.pdh)
        """
        limit_old = self.pdh.pattern_data.df.iloc[-1][CN.POSITION]
        if limit_old < limit:
            print('{}: get_extended_pdh: limit_old={}, limit_new={}'.format(
                ticker_id, limit_old, limit))
            self.init_pattern_data_handler_for_ticker_id(ticker_id=ticker_id, and_clause='', limit=limit)
        return self.pdh

    def init_pattern_data_handler_for_ticker_id(self, ticker_id: str, and_clause: str, limit=300, offset: int=0):
        self.data_provider.init_pattern_data_handler_for_ticker_id(ticker_id, and_clause, limit, offset=offset)
        self.__update_runtime_parameters__()

    def update_data_provider_api(self, from_db: bool=None, period: str=None, aggregation: int=None):
        if from_db is not None:
            self.data_provider.from_db = from_db
        if period is not None:
            self.data_provider.period = period
        if aggregation is not None:
            self.data_provider.aggregation = aggregation

    def get_semi_deep_copy(self):
        """
        This function is necessary since _db_stock can't be deeply copied - I don't know the reason...
        All other components don't make any problems. But nevertheless with this function we have control
        about which part has to be deeply copied and which can be used by reference.
        """
        sys_config_copy = SystemConfiguration(True)

        sys_config_copy.config = deepcopy(self.config)  # we change save modes... ToDo ???
        sys_config_copy.exchange_config = deepcopy(self.exchange_config)  # we change the simulation mode... ToDo ???
        sys_config_copy.file_log = self.file_log
        sys_config_copy.process_manager = self.process_manager
        sys_config_copy.index_config = self.index_config
        sys_config_copy.pattern_table = self.pattern_table
        sys_config_copy.db_stock = self.db_stock
        sys_config_copy.trade_table = self.trade_table
        sys_config_copy.wave_table = self.wave_table
        sys_config_copy.asset_table = self.asset_table
        sys_config_copy.pattern_table = self.pattern_table
        sys_config_copy.df_cache = self.df_cache
        sys_config_copy.graph_cache = self.graph_cache
        sys_config_copy.data_provider = PatternDataProvider(
            sys_config_copy.config, sys_config_copy.index_config, self.db_stock, self.df_cache)
        sys_config_copy.data_provider.period = self.data_provider.period
        sys_config_copy.data_provider.aggregation = self.data_provider.aggregation
        sys_config_copy.data_provider.output_size = self.data_provider.output_size
        sys_config_copy.data_provider.limit = self.data_provider.limit
        sys_config_copy.data_provider.init_and_clause()
        # print('get_semi_deep_copy: sys_config_copy.data_provider.and_clause={}'.format(sys_config_copy.data_provider.and_clause))
        sys_config_copy.data_provider.ticker_dict = self.data_provider.ticker_dict  # we have to copy this as well
        sys_config_copy.predictor_optimizer = self.predictor_optimizer  # we use the same optimizer  !!!
        sys_config_copy.fibonacci_predictor = self.fibonacci_predictor
        sys_config_copy.fibonacci_wave_data_handler = self.fibonacci_wave_data_handler
        sys_config_copy.master_predictor_handler = PatternMasterPredictorHandler(
            self.__get_pattern_predictor_api__(sys_config_copy.config))
        sys_config_copy.trade_strategy_optimizer = self.trade_strategy_optimizer
        return sys_config_copy

    def __update_runtime_parameters__(self):
        self.runtime_config.actual_ticker = self.data_provider.ticker_id
        self.runtime_config.actual_ticker_name = self.data_provider.ticker_name
        self.runtime_config.actual_ticker_equity_type = self.data_provider.equity_type
        self.runtime_config.actual_expected_win_pct = self.expected_win_pct
        self.runtime_config.actual_and_clause = self.data_provider.and_clause

    def print(self):
        source = 'DB' if self.from_db else 'Api'
        pattern_type = self.config.pattern_type_list
        and_clause = self.data_provider.and_clause
        period = self.period
        output_size = self.data_provider.output_size
        bound_upper_v = self.config.bound_upper_value
        bound_lower_v = self.config.bound_lower_value
        breakout_over_big_range = self.config.breakout_over_congestion_range

        print('\nConfiguration settings:')
        if self.from_db:
            print('Formation: {} \nSource: {} \nAnd clause: {} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, and_clause, bound_upper_v, bound_lower_v, breakout_over_big_range))
        else:
            print('Formation: {} \nSource: {} \n\nPeriod/Output size: {}/{} \nUpper/Lower Bound Value: {}/{}'
                  ' \nBreakout big range: {}\n'.format(
                    pattern_type, source, period, output_size, bound_upper_v, bound_lower_v, breakout_over_big_range))

    def get_time_stamp_before_one_period_aggregation(self, time_stamp: float):
        return time_stamp - self.get_seconds_for_one_period()

    def get_time_stamp_after_ticks(self, tick_number: int, ts_set_off = MyDate.get_epoch_seconds_from_datetime()):
        return int(ts_set_off + tick_number * self.get_seconds_for_one_period())

    def get_seconds_for_one_period(self):
        return MyDate.get_seconds_for_period_aggregation(self.period, self.period_aggregation)

    def init_by_nearest_neighbor_id(self, nn_id: str):  # example: 128#1_1_1_AAPL_12_2015-12-03_00:00_2016-01-07_00:00
        id_components = nn_id.split('#')
        self.init_by_pattern_id_str(id_components[1])

    def init_by_indicator(self, indicator: list):  # example: ['BTCUSD', 15]
        symbol = indicator[0]
        self.data_provider.from_db = False
        self.data_provider.period = PRD.INTRADAY
        self.data_provider.aggregation = indicator[1]
        self.data_provider.use_own_dic({symbol: symbol})

    def init_by_pattern_id_str(self, pattern_id: str):  # example: 1_1_1_AAPL_12_2015-12-03_00:00_2016-01-07_00:00
        pattern_id_obj = PatternID(**{'pattern_id': pattern_id})
        symbol = pattern_id_obj.ticker_id
        self.data_provider.from_db = True
        self.data_provider.period = pattern_id_obj.period
        self.data_provider.aggregation = pattern_id_obj.aggregation
        self.data_provider.use_own_dic({symbol: symbol})
        self.config.pattern_type_list = [pattern_id_obj.pattern_type]
        range_adjusting = max(60, pattern_id_obj.range_length)
        date_from_adjusted = MyDate.adjust_by_days(pattern_id_obj.date_start, -range_adjusting)
        date_to_adjusted = MyDate.adjust_by_days(pattern_id_obj.date_end, 2*range_adjusting)
        self.data_provider.and_clause = "Date BETWEEN '{}' AND '{}'".format(date_from_adjusted, date_to_adjusted)
        self.runtime_config.actual_pattern_range_from_time_stamp = pattern_id_obj.ts_from
        self.runtime_config.actual_pattern_range_to_time_stamp = pattern_id_obj.ts_to


debugger = PatternDebugger()

# Todo Signals and expected win & connection to Bitfinex
"""
ToDo list:
a) Signals - later: With support from KI
- Breakout (differ between false breakout and real breakout
- pullback: within a range (opposite from "expected" breakout) and Fibonacci compliant, i.e. 5th wave completed
b) Expected win for all these case
c) Channel Pattern: sometimes (???) there are only 2 hits on the entrance side and 3 or more on the opposite (breakout)
side - so I think we have to go back with the f_params to the left side as well...
d) Connection to Bitfinex (from 01.09.2018): https://www.bitfinex.com/posts/267
e) Correlation: Please check BCH_USD and EOS - both had TKEs together....
"""