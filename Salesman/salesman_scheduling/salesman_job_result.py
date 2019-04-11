"""
Description: This module contains all the job result classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""

from sertl_analytics.processes.my_job_result import JobResult


class SalesmanDatabaseUpdateJobResult(JobResult):
    def __init__(self):
        JobResult.__init__(self)
        self.number_saved_records = 0

    @property
    def job_details(self):
        return 'Processed/saved record: {}/{}, comment={}'.format(
            self.number_processed_records, self.number_saved_records, self.comment)
