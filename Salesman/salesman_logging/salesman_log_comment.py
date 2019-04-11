"""
Description: This module contains a class for separating a log comment
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-09
Examples:
a) Breakout-Expected_win-Trailing_stop-mean08_INTRADAY_ETHUSD_Triangle down_2019-04-08_21:00_2019-04-09_05:30 (REAL): Stop_loss Result: -0.4
b) Breakout-Expected_win-Limit-mean04_INTRADAY_LTCUSD_Triangle_2019-02-19_01:30_2019-02-19_09:00
"""


from sertl_analytics.constants.pattern_constants import LOGDC, PRD, FT


class LogComment:
    def __init__(self, comment: str):
        self._comment = comment
        self._components_underscore = self._comment.split('_')
        self._components_colon = self._comment.split(':')
        self._idx_intraday_daily = self.__get_idx_intraday_daily__()
        self._idx_symbol = self._idx_intraday_daily + 1
        self._idx_pattern = self._idx_intraday_daily + 2
        self._len_pattern_type = self.__get_length_pattern_type__()
        self._idx_start_dt = self._idx_intraday_daily + 3 + (self._len_pattern_type - 1)
        self._idx_start_time = self._idx_intraday_daily + 4 + (self._len_pattern_type - 1)
        self._idx_end_dt = self._idx_intraday_daily + 5 + (self._len_pattern_type - 1)
        self._idx_end_time = self._idx_intraday_daily + 6 + (self._len_pattern_type - 1)

    def __get_length_pattern_type__(self) -> int:
        pattern_to_check = '{}_{}'.format(self._components_underscore[self._idx_pattern],
                                          self._components_underscore[self._idx_pattern + 1])
        return 2 if pattern_to_check in FT.get_all() else 1

    def get_value_for_log_column(self, log_column: str):
        if log_column == LOGDC.SYMBOL:
            return self._components_underscore[self._idx_symbol]
        elif log_column == LOGDC.PATTERN:
            if self._len_pattern_type == 2:
                return '{}_{}'.format(self._components_underscore[self._idx_pattern],
                                      self._components_underscore[self._idx_pattern + 1])
            return self._components_underscore[self._idx_pattern]
        elif log_column == LOGDC.START:
            return self._components_underscore[self._idx_start_time]
        elif log_column == LOGDC.END:
            return self._components_underscore[self._idx_end_time][:5]
        elif log_column == LOGDC.TRADE_TYPE:
            if self._comment.find('(') >= 0 and self._comment.find(')')>= 0:
                return self._comment[self._comment.find('(') + 1:self._comment.find(')')]
        elif log_column == LOGDC.RESULT:
            if self._comment.find('Result:') > 0:
                return '{:.2f}%'.format(float(self._components_colon[-1]))
        return ''

    def __get_idx_intraday_daily__(self):
        for idx, component in enumerate(self._components_underscore):
            if component in [PRD.DAILY, PRD.INTRADAY]:
                return idx
        return -1

