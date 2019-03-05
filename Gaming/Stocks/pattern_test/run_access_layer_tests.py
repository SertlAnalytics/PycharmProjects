"""
Description: This module contains test cases for access layer methods
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_database.stock_access_layer import AccessLayer4Wave, AccessLayer4Stock
from pattern_index_configuration import IndexConfiguration
from pattern_database.stock_database import StockDatabase
from pandas import ExcelWriter
from sertl_analytics.constants.pattern_constants import DC, INDICES

db_stock = StockDatabase()
access_layer_wave = AccessLayer4Wave(db_stock)
# access_layer_stock = AccessLayer4Stock(db_stock)
# writer = ExcelWriter('PythonExport.xlsx')
#
# df_return = access_layer_wave.get_wave_data_frame_with_corresponding_daily_wave_data(
#     period_id=1, days=30)
# print(df_return.describe())
# df_return.to_excel(writer,'MultipleWave')
# writer.save()

index_config = IndexConfiguration(db_stock, [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100])


def get_index_for_symbol(ticker_id: str):
    print(ticker_id)
    return index_config.get_index_for_symbol(ticker_id)

df = access_layer_wave.get_all_as_data_frame()
df[DC.INDEX] = df[DC.TICKER_ID].apply(get_index_for_symbol)
print(df.head())

# df_return = access_layer_wave.get_intraday_wave_data_frame_with_corresponding_daily_wave_data()
# ts_period_daily = 60 * 60 * 24  # 10 days
# for index, row in df_return.iterrows():
#     ts_from = row[DC.WAVE_END_TS] - ts_period_daily * 2
#     ts_to = ts_from + ts_period_daily * 10
#     query = "SELECT * from Stocks WHERE Symbol = '{}' and Timestamp between {} and {}".format(
#         row[DC.TICKER_ID], ts_from, ts_to
#     )
#     df_stocks = access_layer_stock.select_data_by_query(query)
#     print(row)
#     print(df_stocks.head(10))
