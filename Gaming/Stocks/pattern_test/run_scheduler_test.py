"""
Description: This module contains the trade test for the scheduler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from sertl_analytics.constants.pattern_constants import PRD
from pattern_scheduling.pattern_job import MyPatternJob, MySecondJob
from pattern_scheduling.pattern_scheduler import MyPatternScheduler
from pattern_dash.my_dash_job_handler import MyDashJobHandler
from time import sleep
from sertl_analytics.mydates import MyDate


scheduler_run_interval_sec = 10
dt_now = MyDate.get_datetime_object()
dt_start_01 = MyDate.adjust_by_seconds(dt_now, 10)
dt_start_02 = MyDate.adjust_by_seconds(dt_start_01, scheduler_run_interval_sec)
start_time_01 = str(dt_start_01.time())[:8]
start_time_02 = str(dt_start_02.time())[:8]
# start_time_list = [start_time_01, start_time_02]
start_time_list = [start_time_02]
weekday_list = [0, 1, 2, 3, 4, 5, 6]

for_dash_test = False
if for_dash_test:
    my_handler = MyDashJobHandler(for_test=True)
    my_handler.check_scheduler_tasks()
else:
    scheduler = MyPatternScheduler('PatternSchedulerTest', for_test=True)
    scheduler.add_job(MyPatternJob(period=PRD.DAILY, weekdays=weekday_list, start_times=start_time_list))
    # scheduler.add_job(MySecondJob(period=PRD.DAILY, weekdays=weekday_list, start_time=start_time))
    for k in range(5):
        scheduler.check_tasks()
        print('{}: Waiting main process for {} seconds...'.format(
            MyDate.get_date_time_as_string_from_date_time(), scheduler_run_interval_sec))
        sleep(scheduler_run_interval_sec)