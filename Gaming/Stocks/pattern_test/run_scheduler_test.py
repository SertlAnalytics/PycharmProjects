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

time_str = '11:00'
diff = MyDate.get_time_difference_to_now_in_minutes(time_str)
dt_now = MyDate.get_datetime_object()
dt_now = MyDate.adjust_by_seconds(dt_now, 10)
start_time = str(dt_now.time())[:8]

for_dash_test = True
if for_dash_test:
    my_handler = MyDashJobHandler(1, for_test=True)
    my_handler.start_scheduler()
else:
    scheduler = MyPatternScheduler(1)
    scheduler.add_job(MyPatternJob(period=PRD.DAILY, weekdays=[0, 1, 2], start_time=start_time))
    scheduler.add_job(MySecondJob(period=PRD.DAILY, weekdays=[0, 1, 2], start_time=start_time))
    scheduler.start_scheduler()

for k in range(10):
    print('Waiting main process for 10 seconds...')
    sleep(10)