"""
Description: This module is the base class for our dash - deferred classes required.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""

from dash import Dash
import pandas as pd
import dash_auth
from sertl_analytics.mypasswords import MyPasswordHandler


class MyDashBase:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.app = Dash()
        self.app.config.suppress_callback_exceptions = True
        self.auth = dash_auth.BasicAuth(self.app, MyPasswordHandler.get_pw_list(self.app_name))
        if __name__ != '__main__':
            self.server = self.app.server
        self.df = None

    def start_app(self):
        print('get_stock_prices')
        self.__set_app_layout__()
        self.__init_interval_callback__()
        self.__init_hover_over_callback__()
        self.__init_update_graph_callback__()

    def __get_bollinger_band_values__(self, price_df: pd.DataFrame, window_size=10, num_of_std=5):
        rolling_mean = price_df.rolling(window=window_size).mean()
        rolling_std = price_df.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return [rolling_mean, upper_band, lower_band]

    def __set_app_layout__(self):
        pass

    def run_on_server(self):
        self.app.run_server()

    def __init_update_graph_callback__(self):
        pass

    def __init_hover_over_callback__(self):
        pass

    def __init_interval_callback__(self):
        pass