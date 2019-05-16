"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import shelve
import os
from files.file_handler import FileHandler


class FileHandlerForCache(FileHandler):
    @staticmethod
    def __get_package_dir__():
        return os.path.abspath(os.path.dirname(__file__))


class CKEY:  # cache keys
    SEARCH_INPUT = 'SEARCH_INPUT'


class SalesmanShelve:
    def __init__(self):
        self._shelve_cache = shelve.open(FileHandlerForCache().get_file_path_for_file('salesman_cache'))

    def get_value(self, key):
        return self._shelve_cache.get(key, '') if key in self._shelve_cache else ''

    def set_value(self, key: str, value):
        self._shelve_cache[key] = value

    def reset(self, key: str):
        if key in self._shelve_cache:
            self._shelve_cache[key] = ''

    def clear(self):
        self._shelve_cache.clear()
