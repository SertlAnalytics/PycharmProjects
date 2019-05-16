"""
Description: This module contains the central file handler class - responsible for file paths
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import os


class FileHandler:
    def __init__(self):
        pass

    def get_file_path_for_file(self, file_name: str):
        package_dir = self.__get_package_dir__()
        # print('get_file_path_for_file: {}'.format(os.path.join(package_dir, file_name)))
        return os.path.join(package_dir, file_name)

    @staticmethod
    def __get_package_dir__():
        return os.path.abspath(os.path.dirname(__file__))

