"""
Description: This module contains the dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""


from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Wave
from sertl_analytics.constants.pattern_constants import PRD, INDICES, LOGT, LOGDC, DC, PRDC, PSC
from sertl_analytics.mydates import MyDate
import pandas as pd

def change_to_date_str(value):
    return str(value)[:10]


db_stock = StockDatabase()
access_layer = AccessLayer4Wave(db_stock)
print(MyDate.time_stamp_now())
df = access_layer.get_all_as_data_frame()
print(MyDate.time_stamp_now())
df_grouped_direct_daily = access_layer.get_grouped_by_for_wave_peak_plotting(PRD.DAILY)
print(MyDate.time_stamp_now())
df_grouped_direct_intraday = access_layer.get_grouped_by_for_wave_peak_plotting(PRD.INTRADAY)
for index, row in df_grouped_direct_intraday.iterrows():
    print(row)
print(MyDate.time_stamp_now())

for_grouping = False

if for_grouping:
    df['Date'] = df[DC.WAVE_END_DT].apply(MyDate.get_date_str_from_datetime)
    df_for_grouping = df[[DC.INDEX, DC.PERIOD, DC.WAVE_TYPE, 'Date', DC.TICKER_ID]]
    df_grouped = df_for_grouping.groupby([DC.INDEX, DC.PERIOD, DC.WAVE_TYPE, 'Date']).count()

    df_grouped_direct = access_layer.get_grouped_by_for_wave_plotting()
    pd.DataFrame.to_excel(df_grouped_direct, 'Wave_Grouped.xlsx')
    print('test')
else:
    today_str = MyDate.get_date_as_string_from_date_time()


