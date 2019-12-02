"""
Description: This module contains test cases for access layer methods
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_database.stock_index_data_frame import IndexDataFrame
from pattern_database.stock_database import StockDatabase

db_stock = StockDatabase()
index_data_frame = IndexDataFrame(db_stock)

index_data_frame.print_details()
# index_data_frame.get_index_data_frame_for_date_range('2019-01-01', '2020-01-01')
