"""
Description: This module contains the central pattern file_log class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""
from sertl_analytics.constants.pattern_constants import LOGDC, LOGT, DC, FT
from sertl_analytics.myfilelog import FileLog, FileLogLine
from pattern_logging.pattern_log_comment import LogComment
import os
import pandas as pd


class DataFrameErrorLog:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._df_winner = df[df[DC.TRADE_RESULT_ID] == 1]
        self._df_loser = df[df[DC.TRADE_RESULT_ID] != 1]
        self._df_winner_real = self._df_winner[self._df_winner[DC.TRADE_PROCESS] == 'REAL']
        self._df_loser_real = self._df_loser[self._df_loser[DC.TRADE_PROCESS] == 'REAL']
        self._df_winner_sim = self._df_winner[self._df_winner[DC.TRADE_PROCESS] != 'REAL']
        self._df_loser_sim = self._df_loser[self._df_loser[DC.TRADE_PROCESS] != 'REAL']

    @property
    def numbers_winner(self):
        return self.__get_numbers_for_df__(self._df_winner)

    @property
    def numbers_loser(self):
        return self.__get_numbers_for_df__(self._df_loser)

    @property
    def numbers_winner_real(self):
        return self.__get_numbers_for_df__(self._df_winner_real)

    @property
    def numbers_loser_real(self):
        return self.__get_numbers_for_df__(self._df_loser_real)

    @property
    def numbers_winner_simulation(self):
        return self.__get_numbers_for_df__(self._df_winner_sim)

    @property
    def numbers_loser_simulation(self):
        return self.__get_numbers_for_df__(self._df_loser_sim)

    @staticmethod
    def __get_numbers_for_df__(df: pd.DataFrame):
        return [0, 0] if df.shape[0] == 0 else [df.shape[0], df[DC.TRADE_RESULT_PCT].mean()]


class PatternLog(FileLog):
    @property
    def columns_for_trade_log_table(self):
        return [DC.PATTERN_RANGE_BEGIN_DT, DC.SELL_TIME, 'Process', 'Step', DC.TICKER_ID,
                DC.PATTERN_TYPE, DC.TRADE_STRATEGY,
                DC.PATTERN_RANGE_BEGIN_TIME, DC.PATTERN_RANGE_END_TIME, DC.TRADE_PROCESS,
                DC.TRADE_RESULT_PCT, DC.TRADE_RESULT, DC.TRADE_RESULT_ID]

    def __get_file_path_for_messages__(self):
        return self.__get_file_path__('pattern_log.csv')

    def __get_file_path_for_errors__(self):
        return self.__get_file_path__('pattern_log_errors.csv')

    def __get_file_path_for_scheduler__(self):
        return self.__get_file_path__('pattern_log_scheduler.csv')

    def __get_file_path_for_test__(self):
        return self.__get_file_path__('pattern_log_test.csv')

    def __get_file_path_for_trades__(self):
        return self.__get_file_path__('pattern_log_trades.csv')

    def __get_file_path__(self, file_name: str):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, file_name)

    def get_data_frame_for_trades(self, pattern_type=FT.ALL):
        data_dict = {column: [] for column in self.columns_for_trade_log_table}
        with open(self.__get_file_path_for_trades__(), 'r') as file:
            for line in file.readlines():
                self.__add_trade_line_to_data_dict__(data_dict, line)
        df = pd.DataFrame.from_dict(data_dict)
        if pattern_type != FT.ALL:
            df = df[df[DC.PATTERN_TYPE] == pattern_type]
        df = df[self.columns_for_trade_log_table]  # to have the correct order
        # print(df.head())
        return df

    def get_data_frame_for_error_log(self, pattern_type=FT.ALL) -> DataFrameErrorLog:
        return DataFrameErrorLog(self.get_data_frame_for_trades(pattern_type))

    @staticmethod
    def __add_trade_line_to_data_dict__(data_dict, line: str):
        log_line = FileLogLine(line)
        if log_line.step != 'Sell':
            return
        comment_obj = LogComment(log_line.comment)
        if comment_obj.result == '':
            return
        data_dict[DC.PATTERN_RANGE_BEGIN_DT].append(log_line.date_time)
        data_dict[DC.SELL_TIME].append(log_line.time)
        data_dict['Process'].append(log_line.process)
        data_dict['Step'].append(log_line.step)
        data_dict[DC.TICKER_ID].append(comment_obj.symbol)
        data_dict[DC.PATTERN_TYPE].append(comment_obj.pattern)
        data_dict[DC.TRADE_STRATEGY].append(comment_obj.strategy)
        data_dict[DC.PATTERN_RANGE_BEGIN_TIME].append(comment_obj.start)
        data_dict[DC.PATTERN_RANGE_END_TIME].append(comment_obj.end)
        data_dict[DC.TRADE_PROCESS].append(comment_obj.trade_type)
        data_dict[DC.TRADE_RESULT_PCT].append(comment_obj.result_pct)
        data_dict[DC.TRADE_RESULT].append(comment_obj.result_summary)
        data_dict[DC.TRADE_RESULT_ID].append(comment_obj.result_id)

    def delete_wrong_lines_from_trades_log(self):
        file_path = self.get_file_path_for_log_type(LOGT.TRADES)
        line_to_keep_list = []
        with open(file_path, 'r') as file:
            for line in file.readlines():
                log_line = FileLogLine(line)
                if log_line.is_valid:
                    if log_line.step == 'Sell':
                        comment_obj = LogComment(log_line.comment)
                        if comment_obj.result not in ['', '-100.00%']:
                            line_to_keep_list.append(line)
                    else:
                        line_to_keep_list.append(line)
        self.__replace_file_when_changed__(file_path, line_to_keep_list)

