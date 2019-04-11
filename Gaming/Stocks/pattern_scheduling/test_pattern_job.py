"""
Description: This module contains the job class for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.constants.pattern_constants import PRD, PRDC, JDC, PPR
from pattern_scheduling.pattern_job import MyPatternJob
from pattern_database.stock_database_updater import StockDatabaseUpdater
from sertl_analytics.test.my_test_case import MyTestCase, MyTestCaseHandler


class MyTestPatterJob(MyPatternJob):
    def __init__(self, period: str, weekdays: list, start_times: list):
        MyPatternJob.__init__(self, period, weekdays, start_times)

    def schedule_next_time(self):
        self.__schedule_next_time__()

    def set_start_time(self, start_time: str):
        self._scheduled_start_time = start_time


class TestHandler4MyPatterJob:
    def __init__(self):
        self._weekdays_all = [0, 1, 2, 3, 4, 5, 6]
        self._weekdays_week = [0, 1, 2, 3, 4]  # Monday till Friday
        # self._db_updater = StockDatabaseUpdater()

    def test_schedule_next_time(self):  #  def __schedule_next_time__(self):
        start_times = ['04:30', '10:00', '16:00', '22:00']
        expected_start_time = MyDate.get_nearest_time_in_list(start_times)

        test_case_handler = MyTestCaseHandler('Test_scheduled_next_time for list {}'.format(start_times))

        my_test_pattern_job = MyTestPatterJob(period=PRD.DAILY,  weekdays=self._weekdays_all, start_times=start_times)
        job_start_time = my_test_pattern_job.start_time

        test_case_handler.add_test_case(
            MyTestCase('init_start_time for current time', MyDate.get_time_from_datetime(),
                       expected_start_time, job_start_time))
        for start_time in start_times:
            my_test_pattern_job.set_start_time(start_time)
            my_test_pattern_job.schedule_next_time()
            my_test_case = MyTestCase(
                'schedule_next_time for ', start_time, expected_start_time, my_test_pattern_job.start_time)
            test_case_handler.add_test_case(my_test_case)
        test_case_handler.print_result()


test_handler_pattern_job = TestHandler4MyPatterJob()
test_handler_pattern_job.test_schedule_next_time()




