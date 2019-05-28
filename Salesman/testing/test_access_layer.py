"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from salesman_database.salesman_db import SalesmanDatabase
from sertl_analytics.constants.salesman_constants import SLDC
from testing.test_data import SaleTestDataFactory


class AccessLayer4SaleTest(AccessLayer4Sale):
    def test_insert_similar_sales(self):
        pass

    def test_get_number_existing_sales_group_by_as_dict(self):
        status_dict = self.get_number_existing_sales_group_by_as_dict([SLDC.SALE_STATE])
        print('status_dict={}'.format(status_dict))

    def test_get_number_existing_sale_relations_group_by_as_dict(self):
        end_date_dict = self.get_number_existing_sale_relations_group_by_as_dict([SLDC.END_DATE])
        print('end_date_dict={}'.format(end_date_dict))



access_layer = AccessLayer4SaleTest(SalesmanDatabase())
# new_version = access_layer.get_next_version_for_sale_id('24840417')
# print('New version = {}'.format(new_version))
access_layer.test_get_number_existing_sale_relations_group_by_as_dict()


