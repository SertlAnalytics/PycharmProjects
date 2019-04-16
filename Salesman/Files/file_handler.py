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

    @staticmethod
    def get_file_path_for_file(file_name: str):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, file_name)

