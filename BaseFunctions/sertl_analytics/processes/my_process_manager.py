"""
Description: This module contains the PatternProcess and PatternProcessManager classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.processes.my_process import MyProcess, ProcessRunUndefinedProcess


class MyProcessManager:
    def __init__(self):
        self._db = self.__get_db__()
        self._process_dict = self.__get_process_dict__()
        self.__set_child_processes__()
        self._default_process = self.__get_default_process__()

    def get_process_by_name(self, process_name: str) -> MyProcess:
        return self._process_dict.get(process_name, self._default_process)

    def print_statistics(self):
        for key, process in self._process_dict.items():
            statistics = process.get_statistics()
            if statistics != '':
                print('Statistics for {}: {}'.format(key, statistics))

    def __get_db__(self):
        pass

    def __get_default_process__(self):
        return ProcessRunUndefinedProcess(self._db)

    def __get_process_dict__(self) -> dict:
        return {}

    def __set_child_processes__(self):
        for process in self._process_dict.values():
            process.set_child_processes(self._process_dict)