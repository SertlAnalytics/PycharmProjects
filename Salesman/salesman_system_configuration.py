"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from salesman_logging.salesman_log import SalesmanLog
from salesman_database.salesman_db import SalesmanDatabase
from salesman_database.salesman_tables import SaleTable, CompanyTable, ProcessTable
from salesman_database.access_layer.access_layer_sale import AccessLayer4Sale
from salesman_sound.salesman_sound_machine import SalesmanSoundMachine
from salesman_logging.salesman_debugger import SalesmanDebugger
from Files.file_handler import FileHandler


class SystemConfiguration:
    def __init__(self, for_semi_deep_copy=False):
        self.file_log = SalesmanLog()
        self.file_handler = FileHandler()
        self.virtual_sales_file_name = "virtual_sales.csv"
        self.sales_result_file_name = "sales_result.xlsx"
        self.virtual_sales_result_file_name = "virtual_sales_result.xlsx"
        self.sound_machine = SalesmanSoundMachine()
        self.db = SalesmanDatabase()
        self.access_layer_sale = AccessLayer4Sale(self.db)
        self.sale_table = SaleTable()
        self.company_table = CompanyTable()
        self.process_table = ProcessTable()
        self.with_nlp = True
        self.load_sm = True
        self.write_to_excel = False
        self.write_to_database = False
        self.outlier_threshold = 25  # percentile below this threshold and above on top, i.e. < 15 and above 85 for 15

    @property
    def virtual_sales_file_path(self):
        return self.file_handler.get_file_path_for_file(self.virtual_sales_file_name)

    @staticmethod
    def deactivate_log_and_database():
        SalesmanLog.log_activated = False
        SalesmanDatabase.database_activated = False


debugger = SalesmanDebugger()
