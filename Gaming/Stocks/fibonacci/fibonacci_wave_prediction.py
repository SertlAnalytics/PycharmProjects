"""
Description: This module contains the prediction class for fibonacci waves
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-02-26
"""

from sertl_analytics.constants.pattern_constants import DC, FD, PRD
from sertl_analytics.mymath import MyMath
from pattern_database.stock_tables_data_dictionary import WaveDataDictionary
from sertl_analytics.mydates import MyDate


class FibonacciPrediction:
    def __init__(self, data_dict_obj: WaveDataDictionary):
        self.wave_type = data_dict_obj.get(DC.WAVE_TYPE)
        self.period = data_dict_obj.get(DC.PERIOD)
        self.wave_begin_ts = data_dict_obj.get(DC.W1_BEGIN_TS)
        self.wave_end_ts = data_dict_obj.get(DC.WAVE_END_TS)
        self.wave_begin_value = data_dict_obj.get(DC.W1_BEGIN_VALUE)
        self.wave_end_value = data_dict_obj.get(DC.WAVE_END_VALUE)
        self.value_range = abs(self.wave_end_value - self.wave_begin_value)
        self.ts_range = self.wave_end_ts - self.wave_begin_ts
        self.wave_end_flag_pct = data_dict_obj.get('{}{}'.format(self.prefix, DC.WAVE_END_FLAG)) * 100
        self.max_retr_ts_pct = data_dict_obj.get('{}{}'.format(self.prefix, DC.WAVE_MAX_RETR_TS_PCT))
        self.max_retr_pct = data_dict_obj.get('{}{}'.format(self.prefix, DC.WAVE_MAX_RETR_PCT))
        self.wave_end_flag = 'True' if self.wave_end_flag_pct > 0.6 else 'False'
        self.max_retr_ts = self.get_timestamp_for_retracement_pct(self.max_retr_ts_pct)
        self.max_retr_dt = self.get_date_time_for_retracement_pct(self.max_retr_ts_pct)
        self.max_retr = self.get_value_for_retracement_pct(self.max_retr_pct)

    @property
    def prefix(self):
        return 'FC_R_'

    def get_values_for_print_as_list(self):
        wave_end_probability = 'End prob.: {:.2f}%'.format(self.wave_end_flag_pct)
        return [[wave_end_probability, '{:.2f}%'.format(self.max_retr_pct), '{:.2f}%'.format(self.max_retr_ts_pct)],
                [self.wave_end_flag, self.max_retr, self.max_retr_dt]]

    def get_value_for_retracement_pct(self, retracement_pct: float) -> float:
        if self.wave_type == FD.ASC:
            return MyMath.round_smart(self.wave_end_value - self.value_range * retracement_pct/100)
        return MyMath.round_smart(self.wave_end_value + self.value_range * retracement_pct/100)

    def get_timestamp_for_retracement_pct(self, retracement_pct: float) -> int:
        return int(self.wave_end_ts + self.ts_range * retracement_pct/100)

    def get_date_time_for_retracement_pct(self, retracement_pct: float) -> str:
        ts = self.get_timestamp_for_retracement_pct(retracement_pct)
        if self.period == PRD.DAILY:
            return str(MyDate.get_date_from_epoch_seconds(ts))
        return MyDate.get_date_time_from_epoch_seconds_as_string(ts)

    def get_xy_parameter(self):
        x = self.__get_x_parameter__()
        y = self.__get_y_parameter__()
        xy = list(zip(x, y))
        return xy

    def __get_x_parameter__(self) -> list:
        return [self.wave_end_ts, self.max_retr_ts]

    def __get_y_parameter__(self):
        return [self.wave_end_value, self.max_retr]


class FibonacciClassifierPrediction(FibonacciPrediction):
    @property
    def prefix(self):
        return 'FC_C_'


class FibonacciRegressionPrediction(FibonacciPrediction):
    @property
    def prefix(self):
        return 'FC_R_'
