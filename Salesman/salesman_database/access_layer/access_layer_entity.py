"""
Description: This module contains the access layers for entity_relations and entity itself
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from salesman_database.salesman_tables import EntityCategoryTable
from salesman_database.access_layer.access_layer_base import AccessLayer
from sertl_analytics.constants.salesman_constants import SLDC


class AccessLayer4EntityCategory(AccessLayer):
    def is_entity_key_available(self, entity_list_key: str):
        query = "SELECT * from {} WHERE {}='{}';".format(self.table_name, SLDC.ENTITY_LIST, entity_list_key)
        df = self.__get_data_frame_with_row_id_by_query__(query)
        return df.shape[0] > 0

    def get_existing_category_list(self, entity_list_key: str):
        query = "SELECT * from {} WHERE {}='{}';".format(self.table_name, SLDC.ENTITY_LIST, entity_list_key)
        df = self.__get_data_frame_with_row_id_by_query__(query)
        return '' if df.shape[0] == 0 else df.iloc[0][SLDC.CATEGORY_LIST]

    def delete_existing_entity_list(self, entity_list_key: str) -> int:
        if self.is_entity_key_available(entity_list_key):
            query = "DELETE FROM {} WHERE {}='{}';".format(self._table.name, SLDC.ENTITY_LIST, entity_list_key)
            print(query)
            return self._db.delete_records(query)
        return 0

    def update_category_list(self, entity_list_key: str, category_list_key: str, start_date: str) -> int:
        query = "UPDATE {} SET {} = '{}', {} = '{}' WHERE {}='{}';".format(
            self._table.name, SLDC.CATEGORY_LIST, category_list_key, SLDC.START_DATE, start_date,
            SLDC.ENTITY_LIST, entity_list_key)
        print(query)
        return self._db.update_table_by_statement(self._table.name, query)

    @staticmethod
    def get_insert_dict_for_keys(entity_key: str, category_string: str, start_date: str):
        return {SLDC.ENTITY_LIST: entity_key, SLDC.CATEGORY_LIST: category_string,
                SLDC.START_DATE: start_date, SLDC.COMMENT: ''}

    def __get_table__(self):
        return EntityCategoryTable()


class AccessLayer4Entity(AccessLayer):
    pass  # ToDo
