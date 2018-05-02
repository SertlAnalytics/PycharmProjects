from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date
from sertl_analytics.datafetcher.database_fetcher import BaseDatabase, DatabaseDataFrame
from sertl_analytics.datafetcher.financial_data_fetcher import AlphavantageStockFetcher, ApiPeriod, ApiOutputsize
import pandas as pd
import math
from datetime import datetime


class StockSymbols:
    Apple = 'AAPL'
    Cisco = 'CSCO'
    IBM = 'IBM'
    Tesla = 'TSLA'


class StockDatabase(BaseDatabase):
    def __get_engine__(self):
        return create_engine('sqlite:///MyStocks.sqlite')

    def __get_db_name__(self):
        return 'MyStocks'

    def __get_db_path__(self):
        return 'C:/Users/josef/OneDrive/GitHub/PycharmProjects/Gaming/Stocks/MyStocks.sqlite'

    def import_stock_data(self, symbol: StockSymbols, period: ApiPeriod = ApiPeriod.DAILY
                          , output_size: ApiOutputsize = ApiOutputsize.COMPACT):
        self.delete_records("DELETE from Stocks WHERE Symbol = '" + str(symbol) + "'")
        input_list = self.get_input_values_for_stock_table(period, symbol, output_size)
        self.insert_data_into_table('Stocks', input_list)

    def get_input_values_for_stock_table(self, period, symbol: StockSymbols, output_size: ApiOutputsize):
        stock_fetcher = AlphavantageStockFetcher(symbol, period, output_size)
        df = stock_fetcher.get_data_frame()
        input_list = []
        close_previous = 0
        for dates, row in df.iterrows():
            date = datetime.strptime(dates, '%Y-%m-%d')
            open = float(row["Open"])
            high = float(row["High"])
            low = float(row["Low"])
            close = float(row["Close"])
            volume = float(row["Volume"])
            big_move = False  # default
            direction = 0  # default
            if close_previous != 0:
                if abs((close_previous - close) / close) > 0.03:
                    big_move = True
                    direction = math.copysign(1, close - close_previous)
            close_previous = close

            input_dic = {'Period': str(period), 'Symbol': symbol, 'Date': date,
                         'Open': open, 'High': high, 'Low': low, 'Close': close,
                         'Volume': volume, 'BigMove': big_move, 'Direction': direction}

            input_list.append(input_dic)
        return input_list

    def create_tables(self):
        metadata = MetaData()
        # Define a new table with a name, count, amount, and valid column: data
        data = Table('Stocks', metadata,
                     Column('Period', String(20)),  # MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY
                     Column('Symbol', String(20)),
                     Column('Date', Date()),
                     Column('Open', Float()),
                     Column('High', Float()),
                     Column('Low', Float()),
                     Column('Close', Float()),
                     Column('Volume', Float()),
                     Column('BigMove', Boolean(), default=False),
                     Column('Direction', Integer(), default=0)  # 1 = up, -1 = down, 0 = default (no big move)
                     )

        # Define a new table with a name, count, amount, and valid column: data
        # data = Table('Company', metadata,
        #         Column('Symbol', String(10), unique=True),
        #         Column('Name', String(100), unique=True),
        #         Column('Sector', String(100)),
        #         Column('Year', Integer()),
        #         Column('Revenues', Float()),
        #         Column('Expenses', Float()),
        #         Column('Employees', Float()),
        #         Column('Savings', Float()),
        #         Column('ForcastGrowth', Float())
        #     )

        self.create_database_elements(metadata)
        print(repr(data))

class StockDatabaseDataFrame(DatabaseDataFrame):
    def __init__(self, db: BaseDatabase, symbol: str = '', and_clause: str = ''):
        self.symbol = symbol
        self.statement = "SELECT * from Stocks WHERE Symbol = '" + symbol + "'"
        if and_clause != '':
            self.statement += ' and ' + and_clause
        DatabaseDataFrame.__init__(self, db, self.statement)
        self.df['Date'] = self.df['Date'].apply(pd.to_datetime)
        self.df = self.df.set_index('Date')
        self.column_list = list(self.df.columns.values)
        self.column_list_data = self.get_column_list_data()
        self.column_data = self.get_column_data()
        self.column_volume = self.get_column_volume()
        self.df_data = self.df[self.column_list_data]
        self.df_volume = self.df[self.column_volume]

    def get_column_list_data(self):
        return self.column_list[2:7]

    def get_column_data(self):
        return self.column_list[5]

    def get_column_volume(self):
        return self.column_list[6]


dow_jones_dic_orig = {"MMM": "3M", "AXP": "American", "AAPL": "Apple", "BA": "Boing",
"CAT": "Caterpillar", "CVX": "Chevron", "CSCO": "Cisco", "KO": "Coca-Cola",
"DIS": "Disney", "DWDP": "DowDuPont", "XOM": "Exxon", "GE": "General",
"GS": "Goldman", "HD": "Home", "IBM": "IBM", "INTC": "Intel",
"JNJ": "Johnson", "JPM": "JPMorgan", "MCD": "McDonald's", "MRK": "Merck",
"MSFT": "Microsoft", "NKE": "Nike", "PFE": "Pfizer", "PG": "Procter",
"TRV": "Travelers", "UTX": "United", "UNH": "UnitedHealth", "VZ": "Verizon",
"V": "Visa", "WMT": "Wal-Mart"}

if __name__ == '__main__':
    # fetcher.df, fetcher.df_data, fetcher.column_data,
    #                            fetcher.df_volume, fetcher.column_volume, fetcher.symbol
    stock_db = StockDatabase()
    # for ticker in dow_jones_dic_orig:
    #     print('\nProcessing {} - {}'.format(ticker, dow_jones_dic_orig[ticker]))
    #     stock_db.import_stock_data(ticker, ApiPeriod.DAILY, ApiOutputsize.FULL)
    stock_db.import_stock_data(StockSymbols.IBM, ApiPeriod.DAILY)

    # os.remove('C:/Users/josef/OneDrive/GitHub/PycharmProjects/Gaming/Stocks/MyStocks.sqlite')
    # print('Database {} removed: {}'.format(db_name, db_path))