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

log = PatternLog()
for messages in log_message_list:
    if len(messages) > 1:
        log.log_message(messages[0], messages[1], messages[2])
    else:
        log.log_message(messages[0])
    sleep(1)






