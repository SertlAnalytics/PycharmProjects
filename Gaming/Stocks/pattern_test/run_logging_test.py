"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_logging.pattern_log import PatternLog
from time import sleep


log_message_list = [['message1, with comma and with process', 'process 1', 'start'],
                    ['message2; without comma and without process'],
                    ['message1, with comma and with process', 'process 1', 'end']]

for messages in log_message_list:
    if len(messages) > 1:
        PatternLog.log_test_message(messages[0], messages[1], messages[2])
    else:
        PatternLog.log_test_message(messages[0])
    sleep(1)

try:
    a = 100
    b = 0
    c = a/b
    print('{}/{}={}'.format(a, b, c))
except (IOError, ValueError):
    PatternLog.log_error()
except Exception as e:
    print("An unspecified exception occurred")
    PatternLog.log_error()






