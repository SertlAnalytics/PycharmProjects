"""
Description: This module is the main module for file imports.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""

import pandas as pd
import ftplib
import tempfile


class FileFetcher:
    def __init__(self, file_name: str, **args):
        self.file_name = file_name.lower()
        print('FileFetcher: getting...{}'.format(self.file_name))
        self.__user = 'anonymous'
        self.__email = 'josef.sertl@sertl-analytics.com'
        self.protocol = args['protocol'].lower() if 'protocol' in args else ''
        self.file_type = self.__get_file_type__()
        self.df = self.__read_file_into_data_frame__(**args)

    def __get_file_type__(self):
        return self.file_name[self.file_name.index('.')+1:]

    def __read_file_into_data_frame__(self, **args):
        """
        :param params: na_values='n/a' (np.nan NumPy not a Number), parse_dates=['col_1', 'col_2']
        :return:
        """
        if self.protocol == 'ftp':
            return self.__get_file_by_ftp__(args)
        if self.file_type == 'csv':  # args = na_values='n/a' (np.nan NumPy not a Number), parse_dates=['col_1', 'col_2']
            return pd.read_csv(self.file_name, args)
        elif self.file_type in ['xls', 'xlsx']:  # args = sheet_name='Name' or index or sheet_name=['sheet1', 'sheet2']
            if 'sheet_name' in args:
                return pd.read_excel(self.file_name, sheet_name=args['sheet_name'])
            else:
                return pd.read_excel(self.file_name, args)

    def info(self):
        self.df.info()

    def head(self, rows: int = 5):
        self.df.head(rows)

    def __get_file_by_ftp__(self, args):
        url = args['url']
        user = args['user'] if 'user' in args else self.__user
        email = args['email'] if 'user' in args else self.__email
        ftp = ftplib.FTP(url, user, email)
        if 'dir' in args:
            ftp.cwd(args['dir'])
        with tempfile.TemporaryFile() as temp_file:
            ftp.retrbinary('RETR {}'.format(self.file_name), temp_file.write)
            temp_file.seek(0)
            df = pd.read_csv(temp_file, '|')
        ftp.quit()
        return df


class NasdaqFtpFileFetcher:
    def __init__(self):
        self.__df = self.__get_df_by_file_fetcher__()

    def get_data_frame(self):
        return self.__df

    def __get_df_by_file_fetcher__(self):
        file_fetcher = FileFetcher('nasdaqlisted.txt', protocol='FTP', url='ftp.nasdaqtrader.com', dir='SymbolDirectory')
        return file_fetcher.df


# file_fetcher = FileFetcher('nasdaqlisted.txt', protocol='FTP', url='ftp.nasdaqtrader.com', dir='SymbolDirectory')
# file_fetcher.info()
# file_fetcher.head()






