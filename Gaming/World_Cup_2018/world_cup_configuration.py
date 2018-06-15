"""
Description: This module contains the configuration for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""


class WorldCupConfiguration:
    def __init__(self):
        self.__excel_2014_file = 'Fifa_world_cup_2014_matches.xlsx'
        self.__excel_2014_tabs = ['Fifa_world_cup_2014_matches', 'Ranking']
        self.__excel_2018_file = 'Fifa_world_cup_2018_matches.xlsx'
        self.__excel_2018_tabs = ['Fifa_world_cup_2018_matches', 'Ranking']

    @property
    def excel_2014_tabs(self):
        return self.__excel_2014_tabs

    @property
    def excel_2018_tabs(self):
        return self.__excel_2018_tabs

    def get_excel_2014_file_name(self):
        return self.__excel_2014_file

    def get_excel_2018_file_name(self):
        return self.__excel_2018_file


config = WorldCupConfiguration()