"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from salesman_database.salesman_db import SalesmanDatabase


class AccessLayer4SaleTest(AccessLayer4Sale):
    pass


access_layer = AccessLayer4SaleTest(SalesmanDatabase())
new_version = access_layer.get_next_version_for_sale_id('24840417')
print('New version = {}'.format(new_version))

