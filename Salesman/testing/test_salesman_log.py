"""
Description: This module is the test module for the Tutti application modules
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_logging.salesman_log import SalesmanLog

file_log = SalesmanLog()
counter = file_log.count_rows_for_process_optimize_log_files()
print('Rows in log files: {}'.format(counter))
file_log.process_optimize_log_files()
counter_after_process = file_log.count_rows_for_process_optimize_log_files()
print('...deleted: {}/{} - rest:{}'.format(counter-counter_after_process, counter, counter_after_process))
