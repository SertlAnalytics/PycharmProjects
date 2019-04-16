"""
Description: This module starts the stock database processes (create tables, update data, ...)
CAUTION: This script is NOT saved on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from salesman_database.salesman_db import SalesmanDatabase

salesman_db = SalesmanDatabase()
# salesman_db.create_sale_table()
salesman_db.create_sale_view()

