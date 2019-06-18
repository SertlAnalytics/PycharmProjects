"""
Description: This module contains the test cases for my_text.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-13
"""

from my_text import MyText

test_list = False
if test_list:
    tc_list_01 = '[entry1, entry2, ...]'
    tc_list_01 = '[{entry1, {entry2}, ...}, {entry1, entry2, ...}]'
    list_from_text = MyText.get_list_from_text(tc_list_01)
    print('orig text={}, result_list={}'.format(tc_list_01, list_from_text))
else:
    tc_dict_01 = "{'Validity_Datetime': '2019-06-15 12:00:00', 'Validity_Timestamp': 1560592800, 'Location': 'Bitfinex', 'Equity_Type': 'Crypto_Currencies', 'Equity_Type_ID': 20, 'Equity_ID': 'XRP', 'Equity_Name': 'XRP', 'Quantity': 9980.0, 'Value_Unit': 0, 'Value_Total': 4031.92, 'Currency': 'USD'}"
    tc_dict_01 = "{'Period': 'INTRADAY', 'Aggregation': 15, 'Symbol': 'XRPUSD', 'Timestamp': 1560784500, 'Date': datetime.date(2019, 6, 17), 'Time': datetime.time(17, 15), 'Open': 0.433, 'High': 0.434, 'Low': 0.432, 'Close': 0.434, 'Volume': 169404.0, 'BigMove': False, 'Direction': 0}"
    dict_from_text = MyText.get_dict_from_text(tc_dict_01)
    print('orig text={}, result_dict={}'.format(tc_dict_01, dict_from_text))