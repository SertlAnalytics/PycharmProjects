"""
Description: This module contains the job class for patterns
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-23
"""

from pattern_logging.pattern_log import PatternLog

pattern_log = PatternLog()
df = pattern_log.get_data_frame_for_trades()
# pattern_log.delete_wrong_lines_from_trades_log()
# pattern_log.process_optimize_log_files()




