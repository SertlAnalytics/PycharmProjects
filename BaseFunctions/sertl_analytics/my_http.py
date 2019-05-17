"""
Description: This module contains the math classes for sertl-analytics
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-07-24
"""

import http.client
from sertl_analytics.mydates import MyDate


class MyHttpClient:
    @staticmethod
    def do_we_have_internet_connection() -> bool:
        conn = http.client.HTTPConnection("www.google.com", timeout=5)
        connection_ok = True
        try:
            conn.request("HEAD", "/")
        except:
            connection_ok = False
        finally:
            conn.close()
            return connection_ok

    @staticmethod
    def get_status_message(old_message='') -> str:
        if MyHttpClient.do_we_have_internet_connection():
            return 'OK ({})'.format(MyDate.get_time_from_datetime())
        else:
            if old_message.find('NOT') > -1:
                return old_message
            return 'NOT ok since {}'.format(MyDate.get_time_from_datetime())

