"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, CN, PDP, BT, TSTR, TBT


class PatternConfiguration:
    def __init__(self):
        self.detection_process = PDP.ALL
        self.with_trade_part = True  # we need this configuration for testing touch strategy
        self.with_trading = False
        self.trading_last_price_mean_aggregation = 4  # the number of ticker.last_price which are used for stop loss
        self.simple_moving_average_number = 8
        self.pattern_type_list = [FT.CHANNEL]
        self.pattern_ids_to_find = []
        self.forecasting_group_size = 0  # any number larger than 0 generates forecasts
        self.save_pattern_data = True
        self.save_trade_data = True
        self.save_wave_data = True
        self.replace_existing_trade_data_on_db = False
        self.show_differences_to_stored_features = False
        self.bound_upper_value = CN.HIGH
        self.bound_lower_value = CN.LOW
        self.plot_data = True
        self.plot_min_max = False
        self.plot_only_pattern_with_fibonacci_waves = True
        self.plot_volume = False
        self.plot_breakouts = False
        self.plot_close = False
        self.length_for_global_min_max = 50  # a global minimum or maximum must have at least this number as distance
        self.length_for_global_min_max_fibonacci = 10  # ...for fibonacci
        self.length_for_local_min_max = 2  # a local minimum or maximum must have at least this number as distance
        self.length_for_local_min_max_fibonacci = self.length_for_local_min_max  # fibonacci
        self.fibonacci_tolerance_pct = 0.20  # it works great for 0.20 = 20% tolerance for retracement and regression
        self.fibonacci_detail_print = False
        self.bollinger_band_settings = {'distance': 3, 'window_size': 10, 'num_of_std': 3, 'last_elements': 2}
        self.check_previous_period = False   # default
        self.breakout_over_congestion_range = False
        self.breakout_range_pct = 0.05
        self.investment = 1000
        self.max_pattern_range_length = 50
        self.show_final_statistics = False
        self.statistics_excel_file_name = ''
        self.statistics_constraints_excel_file_name = ''  # ''../pattern_statistics/constraints.xlsx'
        self.prediction_optimizer_date = None
        self.__previous_period_length = 0

    def __get_previous_period_length__(self):
        return self.__previous_period_length

    def __set_previous_period_length__(self, value: int):
        self.__previous_period_length = value

    def set_trade_id_as_pattern_id_to_find(self, trade_id: str):
        # From: Breakout-Expected_win-Limit_fix-mean04_DAILY_PG_Channel_2017-10-25_00:00_2017-11-07_00:00
        # To: 1_1_1_KO_22_2016-07-22_00:00_2016-09-28_00:00
        # return '{}-{}-{}-{}_{}'.format(
        #    self.buy_trigger, self.trade_box_type, self.trade_strategy, mean_aggregation, self.pattern.id_readable)
        # def __get_pattern_id__(self) -> PatternID:
        #     kwargs = {
        #         'equity_type_id': self.data_dict_obj.get(DC.EQUITY_TYPE_ID),
        #         '_period': self.data_dict_obj.get(DC.PERIOD),
        #         '_aggregation': self.data_dict_obj.get(DC.PERIOD_AGGREGATION),
        #         'ticker_id': self.ticker_id,
        #         'pattern_type': self.pattern_type,
        #         'pattern_range_id': self.pattern_range.id
        #     }
        #     return PatternID(**kwargs)
        # [0]: Breakout - Expected_
        # [1]: win - Limit_
        # [2]: fix - mean04_
        # [3]: DAILY_
        # [4]: PG_
        # [5]: Channel_
        # [6]: 2017 - 10 - 25     # _
        # [7]: 00:00        # _
        # [8]: 2017 - 11 - 07        # _
        # [9]: 00:00
        #
        # Breakout - Expected_win - Trailing_stepped_stop - mean04_DAILY_LTCUSD_Channel_2016 - 12 - 0
        # 9_00: 00_2016 - 12 - 17_00:00
        # '10-10-30-DAILY-0-Channel-2016-12-09-00:00-2016-12-17'

        trade_id_parts_01 = trade_id.split('-')
        trade_id_parts_02 = trade_id.split('_')
        buy_trigger_id = BT.get_id(trade_id_parts_01[0])
        trade_box_type_id = TBT.get_id(trade_id_parts_01[1])
        trade_strategy_id = TSTR.get_id(trade_id_parts_01[2])
        symbol = trade_id_parts_02[4]
        pattern_type_id = FT.get_id(trade_id_parts_02[5])
        date_from = trade_id_parts_02[6]
        time_from = trade_id_parts_02[7]
        date_to = trade_id_parts_02[8]
        time_to = trade_id_parts_02[9]
        pattern_id = '-'.join([str(buy_trigger_id), str(trade_box_type_id), str(trade_strategy_id),
                               symbol, str(pattern_type_id),
                               date_from, time_from, date_to, time_to])
        self.pattern_ids_to_find = [pattern_id]

    previous_period_length = property(__get_previous_period_length__, __set_previous_period_length__)