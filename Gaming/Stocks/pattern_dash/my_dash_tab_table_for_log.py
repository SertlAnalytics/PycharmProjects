"""
Description: This module contains the dash table for most of the logs
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-01
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, DC, LOGT, LOGDC, PRDC, DTRG


class LogRow:
    sort_column = LOGDC.DATE

    def __init__(self, columns: list):
        self._columns = columns
        self._value_dict = {col: '' for col in self._columns}

    @property
    def value_dict(self):
        return self._value_dict

    @property
    def columns(self):
        return self._columns

    @property
    def date(self):
        return self._value_dict[LOGDC.DATE]

    @property
    def time(self):
        return self._value_dict[LOGDC.TIME]

    @property
    def process(self):
        return self._value_dict[LOGDC.PROCESS]

    @property
    def process_step(self):
        return self._value_dict[LOGDC.PROCESS_STEP]

    def add_value(self, column: str, value):
        self._value_dict[column] = value

    def get_row_as_dict(self):
        return self._value_dict

    def __eq__(self, other):
        return self._value_dict[self.sort_column] == other.value_dict[self.sort_column]

    def __lt__(self, other):
        return self._value_dict[self.sort_column] < other.value_dict[self.sort_column]

    def __gt__(self, other):
        return self._value_dict[self.sort_column] < other.value_dict[self.sort_column]


class LogTable:
    def __init__(self, df_dict: dict, log_type: str, date_range: str):
        self._df_dict = df_dict
        self._selected_log_type = log_type
        self._selected_log_process = ''
        self._selected_log_process_step = ''
        self._selected_date_range = date_range
        self._log_df = df_dict[log_type]
        self._columns = self._log_df.columns
        self._date_column = self.__get_date_column__()
        self._sort_column = self.__get_sort_column__()
        self._process_column = self.get_process_column_for_log_type(self._selected_log_type)
        self._process_step_column = self.get_process_step_column_for_log_type(self._selected_log_type)
        self._rows_selected_log_type = []
        self.__init_data_for_selected_items__()

    @property
    def columns(self):
        return self._columns

    @property
    def date_column(self):
        return self._date_column

    @property
    def process_column(self):
        return self._process_column

    @property
    def process_step_column(self):
        return self._process_step_column

    @property
    def height_for_display(self):
        height = max(100, 50 + len(self._rows_selected_log_type) * 40)
        if height > 400:
            return 400
        return max(100, height)

    def get_rows_for_selected_items(self):
        if len(self._rows_selected_log_type) == 0:
            return [LogRow(self._columns).get_row_as_dict()]
        LogRow.sort_column = self._sort_column
        sort_reverse = True
        sorted_list = sorted(self._rows_selected_log_type, reverse=sort_reverse)
        return [row.get_row_as_dict() for row in sorted_list]

    def update_rows_for_selected_log_type(self, df_dict: dict, log_type: str, process: str, step: str, date_range: str):
        self._df_dict = df_dict
        self._selected_log_type = log_type
        self._selected_log_process = '' if process == 'All' else process
        self._selected_log_process_step = '' if step == 'All' else step
        self._selected_date_range = date_range
        self._date_column = self.__get_date_column__()
        self._process_column = self.get_process_column_for_log_type(self._selected_log_type)
        self._process_step_column = self.get_process_step_column_for_log_type(self._selected_log_type)
        if self._selected_log_type == '' or self._selected_log_type not in self._df_dict:
            self._rows_selected_log_type = []
        else:
            self.__init_data_for_selected_items__()

    @staticmethod
    def get_process_column_for_log_type(log_type: str):
        if log_type == LOGT.PROCESSES:
            return PRDC.TRIGGER
        elif log_type == LOGT.WAVES:
            return ''
        elif log_type == LOGT.PATTERNS:
            return ''
        return LOGDC.PROCESS

    @staticmethod
    def get_process_step_column_for_log_type(log_type: str):
        if log_type == LOGT.PROCESSES:
            return ''
        elif log_type == LOGT.WAVES:
            return ''
        elif log_type == LOGT.PATTERNS:
            return ''
        return LOGDC.PROCESS_STEP

    def __init_data_for_selected_items__(self):
        self._log_df = self._df_dict[self._selected_log_type]
        self._columns = self._log_df.columns
        self.__adjust_log_df_to_selected_items__()
        self.__fill_rows_for_selected_log_type__()

    def __get_sort_column__(self):
        if self._selected_log_type == LOGT.PROCESSES:
            return PRDC.START_DT
        elif self._selected_log_type == LOGT.WAVES:
            return DC.W1_BEGIN_DT
        elif self._selected_log_type == LOGT.PATTERNS:
            return DC.TS_PATTERN_TICK_FIRST
        return LOGDC.DATE

    def __adjust_log_df_to_selected_items__(self):
        if self._process_column != '' and self._selected_log_process != '':
            self._log_df = self._log_df[self._log_df[self._process_column] == self._selected_log_process]
        if self._process_step_column != '' and self._selected_log_process_step != '':
            self._log_df = self._log_df[self._log_df[self._process_step_column] == self._selected_log_process_step]
        if self._selected_date_range == DTRG.TODAY:
            if self._date_column == DC.WAVE_END_TS:
                offset_ts = MyDate.get_epoch_seconds_for_date() - MyDate.get_seconds_for_period(days=2)  # minus 2 day
                self._log_df = self._log_df[self._log_df[self._date_column] >= offset_ts]
            elif self._date_column == DC.TS_PATTERN_TICK_LAST:
                offset_ts = MyDate.get_epoch_seconds_for_date() - MyDate.get_seconds_for_period(days=2)  # minus 2 day
                self._log_df = self._log_df[self._log_df[self._date_column] >= offset_ts]
            else:
                today_str = MyDate.get_date_as_string_from_date_time()
                self._log_df = self._log_df[self._log_df[self._date_column] == today_str]

    def __fill_rows_for_selected_log_type__(self):
        self._rows_selected_log_type = []
        if self._selected_log_type != '':
            for index, row in self._log_df.iterrows():
                log_row = LogRow(self._columns)
                for column in self._columns:
                    log_row.add_value(column, row[column])
                self._rows_selected_log_type.append(log_row)

    def __get_date_column__(self):
        if self._selected_log_type == LOGT.PROCESSES:
            return PRDC.START_DT
        elif self._selected_log_type == LOGT.WAVES:
            return DC.WAVE_END_TS
        elif self._selected_log_type == LOGT.PATTERNS:
            return DC.TS_PATTERN_TICK_LAST
        return LOGDC.DATE




