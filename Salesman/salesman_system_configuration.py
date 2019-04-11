"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from salesman_logging.salesman_log import SalesmanLog
from salesman_database.salesman_db import SalesmanDatabase
from salesman_database.salesman_tables import OfferTable, CompanyTable, ProcessTable
from salesman_sound.salesman_sound_machine import SalesmanSoundMachine
from salesman_logging.salesman_debugger import SalesmanDebugger


class SystemConfiguration:
    def __init__(self, for_semi_deep_copy=False):
        self.file_log = SalesmanLog()
        self.sound_machine = SalesmanSoundMachine()
        self.db = SalesmanDatabase()
        self.offer_table = OfferTable()
        self.company_table = CompanyTable()
        self.process_table = ProcessTable()

    @staticmethod
    def deactivate_log_and_database():
        SalesmanLog.log_activated = False
        SalesmanDatabase.database_activated = False


debugger = SalesmanDebugger()
