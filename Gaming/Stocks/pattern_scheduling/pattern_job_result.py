"""
Description: This module contains all the job result classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""


class JobResult:
    def __init__(self):
        self.number_processed_records = 0
        self.number_deleted_records = 0
        self.comment = ''

    @property
    def job_details(self):
        return 'Processed record: {}, comment={}'.format(self.number_processed_records, self.comment)


class StockDatabaseUpdateJobResult(JobResult):
    def __init__(self):
        JobResult.__init__(self)
        self.number_saved_records = 0

    @property
    def job_details(self):
        return 'Processed/saved record: {}/{}, comment={}'.format(
            self.number_processed_records, self.number_saved_records, self.comment)
