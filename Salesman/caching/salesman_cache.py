"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import shelve
import pickle
import os
from files.file_handler import FileHandler
from time import sleep


class FileHandlerForCache(FileHandler):
    @staticmethod
    def __get_package_dir__():
        return os.path.abspath(os.path.dirname(__file__))

    @staticmethod
    def delete_cache_files(filename: str):
        extension_list = ['bak', 'dat', 'dir']
        for extension in extension_list:
            file_path = FileHandlerForCache().get_file_path_for_file('{}.{}'.format(filename, extension))
            if os.path.exists(file_path):
                print('Deleting...{}'.format(file_path))
                os.remove(file_path)
            else:
                print("The file {} does not exist".format(file_path))


class CKEY:  # cache keys
    SEARCH_INPUT = 'SEARCH_INPUT'


class SalesmanShelve:
    def __init__(self):
        self._cache_file_name = 'salesman_cache'
        self._shelve_cache = shelve.open(FileHandlerForCache().get_file_path_for_file(self._cache_file_name))

    def get_value(self, key):
        try:
            return self._shelve_cache.get(key, '') if key in self._shelve_cache else ''
        except pickle.UnpicklingError:
            print('pickle.UnpicklingError => deleting cache files...:')
            FileHandlerForCache.delete_cache_files(self._cache_file_name)
            sleep(1)
            self._shelve_cache = shelve.open(FileHandlerForCache().get_file_path_for_file(self._cache_file_name))
            return ''

    def set_value(self, key: str, value):
        self._shelve_cache[key] = value

    def reset(self, key: str):
        if key in self._shelve_cache:
            self._shelve_cache[key] = ''

    def clear(self):
        self._shelve_cache.clear()
