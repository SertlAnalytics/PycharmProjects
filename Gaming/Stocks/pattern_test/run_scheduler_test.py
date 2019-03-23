"""
Description: This module contains the trade test for the scheduler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from sertl_analytics.constants.pattern_constants import PRD, PPR
from pattern_process_manager import PatternProcessManager, PatternProcess
from pattern_scheduling.pattern_job import MyPatternJob, MySecondJob
from pattern_scheduling.pattern_scheduler import MyPatternScheduler
from pattern_dash.my_dash_job_handler import MyDashJobHandler
from time import sleep
from sertl_analytics.mydates import MyDate

process_manager = PatternProcessManager()
scheduler_run_interval_sec = 10
dt_now = MyDate.get_datetime_object()
dt_start_01 = MyDate.adjust_by_seconds(dt_now, 10)
dt_start_02 = MyDate.adjust_by_seconds(dt_start_01, scheduler_run_interval_sec)
start_time_01 = str(dt_start_01.time())[:8]
start_time_02 = str(dt_start_02.time())[:8]
# start_time_list = [start_time_01, start_time_02]
start_time_list = [start_time_02]
weekday_list = [0, 1, 2, 3, 4, 5, 6]


undefined_process = process_manager.get_process_by_name(PPR.RUN_UNDEFINED_PROCESS)
update_trade_process = process_manager.get_process_by_name(PPR.UPDATE_TRADE_RECORDS)


@undefined_process.process_decorator
def test_function_01(number: int, process=None):
    process.increment_processed_records(5)
    process.increment_inserted_records(3)
    return number * 2


print('test_function_01 = {}, statistics={}'.format(test_function_01(4), undefined_process.get_statistics()))


# @PatternProcessManager.processmethod(update_trade_process)
# def test_function(number: int, process=None):
#     process.increment_processed_records()
#     process.increment_inserted_records()
#     return number * 2
#
#
# print('test_function={}, statistics={}'.format(test_function(4), update_trade_process.get_statistics()))

for_dash_test = False
if for_dash_test:
    my_handler = MyDashJobHandler(process_manager, for_test=True)
    my_handler.check_scheduler_tasks()
else:
    scheduler = MyPatternScheduler('PatternSchedulerTest', process_manager, for_test=True)
    scheduler.add_job(MyPatternJob(period=PRD.DAILY, weekdays=weekday_list, start_times=start_time_list))
    # scheduler.add_job(MySecondJob(period=PRD.DAILY, weekdays=weekday_list, start_time=start_time))
    for k in range(4):
        scheduler.check_tasks()
        print('{}: Waiting main process for {} seconds...'.format(
            MyDate.get_date_time_as_string_from_date_time(), scheduler_run_interval_sec))
        sleep(scheduler_run_interval_sec)
process_manager.print_statistics()