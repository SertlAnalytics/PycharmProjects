"""
Description: This module contains the debugger for pattern code. It stops for certain conditions
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


class PatternDebugger:
    def __init__(self):
        self.__process_dic = {}
        self.pattern_range_position_list = []

    @property
    def is_active(self):
        for process in self.__process_dic:
            if self.__process_dic[process]:
                return True
        return False

    def check_range_position_list(self, position_list: list):
        process = 'position_list'
        self.__init_process__(process)
        min_len = min(len(position_list), len(self.pattern_range_position_list))
        if min_len > 0:
            intersect = set(position_list).intersection(set(self.pattern_range_position_list))
            if len(intersect) == len(self.pattern_range_position_list):
                self.__activate_process__(process)

    def __init_process__(self, process: str):
        self.__process_dic[process] = False

    def __activate_process__(self, process: str):
        self.__process_dic[process] = True

