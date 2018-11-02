"""
Description: This module contains the central news handler class - which is used to transfer news from different
application layers.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-24
"""

from datetime import datetime


class NewsHandler:
    def __init__(self, delimiter='  \n  - ', default=''):
        self._news_dict = {}
        self._delimiter = delimiter
        self._default = default

    @property
    def news_dict(self):
        return self._news_dict

    def add_news(self, title: str, details: str):
        self._news_dict[title] = [details, datetime.now().timestamp()]

    def add_news_dict(self, news_dict: dict):
        for title, value in news_dict.items():
            self._news_dict[title] = value

    def clear(self):
        self._news_dict = {}

    def get_news_for_markdown_since_last_refresh(self, ts_last_refresh):
        # print('NewsHandler: {}'.format(self._news_dict))
        actual_dict = {key: value for key, value in self._news_dict.items() if value[1] > ts_last_refresh}
        if len(actual_dict) == 0:
            self._news_dict = {}  # remove older news...
            return self._default
        news_list = ['**{}**: {}'.format(key, value[0]) for key, value in actual_dict.items()]
        return self._delimiter.join(news_list)