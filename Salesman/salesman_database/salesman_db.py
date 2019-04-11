"""
Description: This module contains the configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.mydates import MyDate
from salesman_database.salesman_tables import OfferTable, CompanyTable, MetricTable, ProcessTable
from sertl_analytics.constants.pattern_constants import STBL
from sertl_analytics.constants.salesman_constants import SMTBL, SMVW, ODC
from salesman_database.salesman_views import OfferView
from salesman_logging.salesman_log import SalesmanLog
from datetime import datetime
from sertl_analytics.datafetcher.database_fetcher import MyTable
from sertl_analytics.constants.pattern_constants import CN, PRD
import os


class SalesmanDatabase(BaseDatabase):
    def __init__(self):
        self._offer_table = OfferTable()
        self._company_table = CompanyTable()
        self._process_table = ProcessTable()
        self._metric_table = MetricTable()
        BaseDatabase.__init__(self)
        self._file_log = SalesmanLog()
        self._dt_now_time_stamp = int(datetime.now().timestamp())
        self._sleep_seconds = 5

    def delete_duplicate_records(self, table: MyTable):
        pass

    def __get_table_dict__(self) -> dict:
        return {SMTBL.OFFER: self._offer_table,
                STBL.PROCESS: self._process_table,
                STBL.COMPANY: self._company_table,
                STBL.METRIC: self._metric_table,
                }

    def __get_db_name__(self):
        return 'MySales.sqlite'

    def __get_db_path__(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, self.__get_db_name__())

    def insert_offer_data(self, input_dict_list: list):
        self.__insert_data_into_table__(SMTBL.OFFER, input_dict_list)

    def insert_company_data(self, input_dict_list: list):
        self.__insert_data_into_table__(STBL.COMPANY, input_dict_list)

    def insert_process_data(self, input_dict_list: list):
        self.__insert_data_into_table__(STBL.PROCESS, input_dict_list)

    def insert_metric_data(self, input_dict_list: list):
        self.__insert_data_into_table__(STBL.METRIC, input_dict_list)

    def insert_data_into_table(self, table_name: str, input_dict_list: list):
        self.__insert_data_into_table__(table_name, input_dict_list)

    def __get_kw_args_for_data_fetcher__(self, period: str, aggregation: int, output_size: str, ticker: str):
        kw_args = {'symbol': ticker, 'period': period, 'aggregation': aggregation, 'output_size': output_size}
        return kw_args

    def create_offer_table(self):
        self.__create_table__(SMTBL.OFFER)

    def create_company_table(self):
        self.__create_table__(STBL.COMPANY)

    def create_metric_table(self):
        self.__create_table__(STBL.METRIC)

    def create_process_table(self):
        self.__create_table__(STBL.PROCESS)

    def create_offer_view(self):
        self.__create_view__(SMVW.V_OFFER)

    def is_offer_already_available(self, offer_id: str) -> bool:
        query = self._offer_table.get_query_select_for_unique_record_by_id(offer_id)
        db_df = DatabaseDataFrame(self, query)
        return db_df.df.shape[0] > 0

    def update_price_change_for_offer(self, offer_id: str, price_new: float):
        where_clause = "Offer_ID = '{}'".format(offer_id)
        query = self._offer_table.get_query_select_for_records(where_clause)
        db_df = DatabaseDataFrame(self, query)
        price_change_old = ''
        price_change_new = '{}: {}'.format(MyDate.get_date_as_string_from_date_time(), price_new)
        self.update_table_column(SMTBL.OFFER, ODC.PRICE_CHANGES, price_change_new, "ID = '{}'".format(offer_id))

    def update_similar_offers(self):
        print('ToDo: update similar offers...')  # ToDo

    def delete_existing_offer(self, offer_id: str):
        if self.is_offer_already_available(offer_id):
            self.delete_records(self._offer_table.get_query_delete_by_id(offer_id))

    @staticmethod
    def __get_view_by_name__(view_name: str):
        return {SMVW.V_OFFER: OfferView()}.get(view_name, None)


class SalesmanDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: SalesmanDatabase, symbol='', and_clause='', period=PRD.DAILY, aggregation=1):
        self.symbol = symbol
        self.statement = "SELECT * from {} WHERE Symbol = '{}' and Period = '{}' and Aggregation = {}".format(
            STBL.STOCKS, symbol, period, aggregation)
        if and_clause != '':
            self.statement += ' and ' + and_clause
        DatabaseDataFrame.__init__(self, db, self.statement)
        if self.df.shape[0] == 0:
            self.df_data = None
        else:
            self.df.set_index(CN.TIMESTAMP, drop=False, inplace=True)
            self.column_data = [CN.CLOSE]
            self.df_data = self.df[[CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL, CN. TIMESTAMP, CN.BIG_MOVE, CN.DIRECTION]]



