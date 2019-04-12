"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from salesman_database.salesman_tables import OfferTable
from salesman_database.access_layer.access_layer_base import AccessLayer
from sertl_analytics.constants.salesman_constants import ODC


class AccessLayer4Offer(AccessLayer):
    def are_any_records_available_for_master_id(self, master_id: str):
        query = "SELECT * from {} WHERE {}='{}' and {}!='{}';".format(
            self.table_name, ODC.OFFER_ID_MASTER, master_id, ODC.OFFER_ID, master_id
        )
        df = self.__get_data_frame_with_row_id_by_query__(query)
        return df.shape[0] > 0

    def get_existing_offers_for_master_id(self, master_id: str):
        query = "SELECT * from {} WHERE {}='{}' and {}!='{}';".format(
            self.table_name, ODC.OFFER_ID_MASTER, master_id, ODC.OFFER_ID, master_id
        )
        return self.select_data_by_query(query)

    def is_offer_with_offer_id_available(self, offer_id: str):
        query = "SELECT * from {} WHERE {}='{}';".format(self.table_name, ODC.OFFER_ID, offer_id)
        df = self.select_data_by_query(query)
        return df.shape[0] > 0

    def get_offer_by_offer_id(self, offer_id: str):
        query = "SELECT * from {} WHERE {}='{}';".format(self.table_name, ODC.OFFER_ID, offer_id)
        return self.select_data_by_query(query)

    def delete_existing_offer_by_offer_id(self, offer_id: str) -> int:
        query = "DELETE FROM {} WHERE {}='{}';".format(self._table.name, ODC.OFFER_ID, offer_id);
        print(query)
        return self._db.delete_records(query)

    def __get_table__(self):
        return OfferTable()