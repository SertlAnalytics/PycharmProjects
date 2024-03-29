"""
Description: This module contains the html header tables for the dash application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03  test update
"""

from sertl_analytics.constants.pattern_constants import LOGT, WAVEST, INDICES
from datetime import datetime
from sertl_analytics.mydates import MyDate
from sertl_analytics.mydash.my_dash_components import MyHTMLTable, COLORS, MyHTML, MyDCC
from sertl_analytics.my_http import MyHttpClient


class MyHTMLHeaderTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 2, 3)

    def _init_cells_(self):
        user_label_div = MyHTML.div('my_user_label_div', 'Username:', True)
        user_div = MyHTML.div('my_user_name_div', 'Josef Sertl', False)
        date_str = MyDate.get_date_str_from_datetime(datetime.now())
        time_str = MyDate.get_time_from_datetime(datetime.now())
        login_label_div = MyHTML.div('my_login_label_div', 'Last login:', True, True)
        login_date_time_div = MyHTML.div('my_login_div', '{} {}'.format(date_str, time_str), False)
        sound_label_div = MyHTML.div('my_sound_label_div', 'Sound:', True, True)
        sound_div = MyHTML.div('my_sound_div', '', False)
        mode_label_div = MyHTML.div('my_mode_label_div', 'Mode:', True, True)
        mode_div = MyHTML.div('my_mode_div', '', False)
        max_buy_label_div = MyHTML.div('my_max_buy_label_div', 'Max buy value:', True, True)
        max_buy_div = MyHTML.div('my_max_buy_div', '', False)
        small_profit_label_div = MyHTML.div('my_small_profit_label_div', 'Small profit taking:', True, True)
        small_profit_div = MyHTML.div('my_small_profit_div', '', False)

        my_user_div = MyHTML.div_embedded([user_label_div, MyHTML.span(' '), user_div])
        my_login_div = MyHTML.div_embedded([login_label_div, MyHTML.span(' '), login_date_time_div])
        my_sound_div = MyHTML.div_embedded([sound_label_div, MyHTML.span(' '), sound_div])
        my_mode_div = MyHTML.div_embedded([mode_label_div, MyHTML.span(' '), mode_div])
        my_max_buy_div = MyHTML.div_embedded([max_buy_label_div, MyHTML.span(' '), max_buy_div])
        my_small_profit_div = MyHTML.div_embedded([small_profit_label_div, MyHTML.span(' '), small_profit_div])

        dash_board_title_div = MyHTML.div('my_dashboard_title_div', 'Pattern Detection Dashboard', inline=False)
        dash_board_sub_title_div = MyHTML.div('my_dashboard_sub_title_div', '', bold=False, color='red')

        time_label_div = MyHTML.div('my_time_label_div', 'Time:', True)
        time_value_div = MyHTML.div('my_time_div', '', False)
        time_div = MyHTML.div_embedded([time_label_div, MyHTML.span(' '), time_value_div])

        last_refresh_label_div = MyHTML.div('my_last_refresh_label_div', 'Last refresh:', True)
        last_refresh_time_div = MyHTML.div('my_last_refresh_time_div', time_str)
        next_refresh_label_div = MyHTML.div('my_next_refresh_label_div', 'Next refresh:', True)
        next_refresh_time_div = MyHTML.div('my_next_refresh_time_div', time_str)
        last_refresh_div = MyHTML.div_embedded([last_refresh_label_div, MyHTML.span(' '), last_refresh_time_div])
        next_refresh_div = MyHTML.div_embedded([next_refresh_label_div, MyHTML.span(' '), next_refresh_time_div])

        http_connection_label_div = MyHTML.div('my_http_connection_label_div', 'Connection:', True, True)
        http_connection_div = MyHTML.div('my_http_connection_div', MyHttpClient.get_status_message(), False)
        my_http_connection_div = MyHTML.div_embedded([http_connection_label_div, MyHTML.span(' '), http_connection_div])

        online_trade_label_div = MyHTML.div('my_online_trade_label_div', 'Trades - Online:', True)
        online_trade_active_div = MyHTML.div('my_online_trade_active_div', '0')
        online_trade_all_div = MyHTML.div('my_online_trade_all_div', '0')

        stored_trade_label_div = MyHTML.div('my_stored_trade_label_div', 'Trades - Replay:', True)
        stored_trade_div = MyHTML.div('my_stored_trade_div', '0')

        stored_pattern_label_div = MyHTML.div('my_stored_pattern_label_div', 'Pattern - Replay:', True)
        stored_pattern_div = MyHTML.div('my_stored_pattern_div', '0')

        trade_div = MyHTML.div_embedded([stored_trade_label_div, MyHTML.span(' '), stored_trade_div])
        pattern_div = MyHTML.div_embedded([stored_pattern_label_div, MyHTML.span(' '), stored_pattern_div])

        real_online_trade_label_div = MyHTML.div('my_real_online_trade_label_div', 'Trades - real:', True)
        real_online_trade_div = MyHTML.div('my_real_online_trade_div', '')
        simulation_online_trade_label_div = MyHTML.div('my_simulation_online_trade_label_div', 'Trades - simul.:', True)
        simulation_online_trade_div = MyHTML.div('my_simulation_online_trade_div', '')

        online_div = MyHTML.div_embedded([
            online_trade_label_div, MyHTML.span(' '),
            online_trade_active_div, MyHTML.span('/'), online_trade_all_div], inline=True)
        real_online_trade_div = MyHTML.div_embedded(
            [real_online_trade_label_div, MyHTML.span(' '), real_online_trade_div])
        simulation_online_trade_div = MyHTML.div_embedded(
            [simulation_online_trade_label_div, MyHTML.span(' '), simulation_online_trade_div])

        self.set_value(1, 1, MyHTML.div_embedded([my_user_div, my_login_div, my_sound_div,
                                                  my_mode_div, my_max_buy_div, my_small_profit_div]))
        self.set_value(1, 2, MyHTML.div_embedded([dash_board_title_div, dash_board_sub_title_div]))
        self.set_value(1, 3, MyHTML.div_embedded([time_div, next_refresh_div, last_refresh_div, my_http_connection_div]))
        self.set_value(2, 1, MyDCC.markdown('my_position_markdown'))
        self.set_value(2, 2, MyDCC.markdown('my_dashboard_markdown'))
        self.set_value(2, 3, MyHTML.div_embedded(
            [online_div, trade_div, pattern_div, real_online_trade_div, simulation_online_trade_div]))

    def _get_cell_style_(self, row: int, col: int):
        width = ['20%', '60%', '20%'][col-1]
        bg_color = COLORS[0]['background']
        color = COLORS[0]['text']
        text_align = [['left', 'center', 'right'], ['left', 'left', 'right']][row - 1][col-1]
        v_align = [['top', 'top', 'top'], ['top', 'top', 'middle']][row - 1][col - 1]
        font_weight = [['normal', 'bold', 'normal'], ['normal', 'normal', 'normal']][row - 1][col - 1]
        font_size = [[16, 32, 16], [14, 14, 14]][row - 1][col - 1]
        padding = 0 if row == 2 and col == 2 else self.padding_cell
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'font-weight': font_weight, 'padding': padding, 'font-size': font_size}


class MyHTMLTabHeaderTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 1, 3)

    def _init_cells_(self):
        self.set_value(1, 1, '')
        self.set_value(1, 2, '')
        self.set_value(1, 3, '')

    def _get_cell_style_(self, row: int, col: int):
        width = ['20%', '60%', '20%'][col - 1]
        bg_color = COLORS[2]['background']
        color = COLORS[2]['text']
        text_align = ['left', 'center', 'left'][col - 1]
        v_align = ['top', 'top', 'top'][col - 1]
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}


class MyHTMLTabPatternHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        ticker_label_div = MyHTML.div('my_ticker_label_div', 'Ticker:', True)
        ticker_div = MyHTML.div('my_ticker_div', '', False)
        self.set_value(1, 1, MyHTML.div_embedded([ticker_label_div, MyHTML.span(' '), ticker_div]))
        self.set_value(1, 2, MyDCC.markdown('my_pattern_markdown'))
        self.set_value(1, 3, '')


class MyHTMLTabPortfolioHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        ticker_label_div = MyHTML.div('my_portfolio_position_label_div', 'Position:', True)
        ticker_div = MyHTML.div('my_portfolio_position_div', '', False)

        self.set_value(1, 1, MyHTML.div_embedded([ticker_label_div, MyHTML.span(' '), ticker_div]))
        self.set_value(1, 2, MyDCC.markdown('my_portfolio_markdown'))
        self.set_value(1, 3, MyDCC.markdown('my_portfolio_news_markdown'))


class MyHTMLTabRecommenderHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        ticker_label_div = MyHTML.div('my_recommender_position_label_div', 'Position:', True)
        ticker_div = MyHTML.div('my_recommender_position_div', '', False)

        self.set_value(1, 1, MyHTML.div_embedded([ticker_label_div, MyHTML.span(' '), ticker_div]))
        self.set_value(1, 2, MyDCC.markdown('my_recommender_markdown'))
        self.set_value(1, 3, MyDCC.markdown('my_recommender_news_markdown'))


class MyHTMLTabLogHeaderTable(MyHTMLTabHeaderTable):
    def __init__(self):
        self._column_number = len(self.__get_table_header_dict__())
        MyHTMLTable.__init__(self, 3, self._column_number)

    def _init_cells_(self):
        column_number = 0
        table_header_dict = self.__get_table_header_dict__()
        today_label_div = MyHTML.div('my_log_today_label_div', 'Today', True)
        all_label_div = MyHTML.div('my_log_all_label_div', 'All', True)
        for log_type, title in table_header_dict.items():
            column_number += 1
            label_div = MyHTML.div('my_log_{}_label_div'.format(log_type), title, True)
            today_value_div = MyHTML.div('my_log_{}_today_value_div'.format(log_type), '0', bold=False)
            all_value_div = MyHTML.div('my_log_{}_all_value_div'.format(log_type), '0', bold=False)
            self.set_value(1, column_number, label_div)
            if log_type == LOGT.DATE_RANGE:
                self.set_value(2, 1, today_label_div)
                self.set_value(3, 1, all_label_div)
            else:
                self.set_value(2, column_number, today_value_div)
                self.set_value(3, column_number, all_value_div)

    @staticmethod
    def get_title_for_log_type(log_type: str):
        table_header_dict = MyHTMLTabLogHeaderTable.__get_table_header_dict__()
        return table_header_dict.get(log_type)

    @staticmethod
    def get_types_for_processing_as_options():
        header_dict = MyHTMLTabLogHeaderTable.__get_table_header_dict__()
        log_types = LOGT.get_log_types_for_processing()
        return [{'label': header_dict[log_type], 'value': log_type} for log_type in log_types]

    @staticmethod
    def __get_table_header_dict__():
        return {LOGT.DATE_RANGE: 'Date range',
                LOGT.ERRORS: 'Errors',
                LOGT.PROCESSES: 'Processes',
                LOGT.SCHEDULER: 'Scheduler',
                LOGT.MESSAGE_LOG: 'Pattern file_log',
                LOGT.PATTERNS: 'Pattern',
                LOGT.WAVES: 'Waves',
                LOGT.TRADES: 'Trades (add/buy)',
                LOGT.TRANSACTIONS: 'Transactions'}

    def _get_cell_style_(self, row: int, col: int):
        base_width = int(100/self._column_number)
        width_list = ['{}%'.format(base_width) for k in range(0, self._column_number)]
        width = width_list[col - 1]
        bg_color = COLORS[2]['background'] if row == 1 or col == 1 else COLORS[1]['background']
        color = COLORS[2]['text']
        text_align = 'left' if col == 1 else 'center'
        v_align = 'top'
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}


class MyHTMLTabWavesHeaderTable(MyHTMLTabHeaderTable):
    def __init__(self):
        self._header_dict = self.__get_table_header_dict__()
        self._column_number = len(self._header_dict)
        self._index_list = INDICES.get_index_list_for_waves_tab()
        MyHTMLTable.__init__(self, len(self._index_list) + 1, self._column_number)

    def _init_cells_(self):
        column_number = 0
        for wave_type, title in self._header_dict.items():
            row_number = 1
            column_number += 1
            label_div = MyHTML.div('my_waves_{}_{}_label_div'.format(row_number, column_number), title, True)
            self.set_value(row_number, column_number, label_div)
            for index in INDICES.get_index_list_for_waves_tab():
                row_number += 1
                if column_number == 1:
                    label_div = MyHTML.div('my_waves_{}_{}_label_div'.format(row_number, column_number), index, True)
                    self.set_value(row_number, column_number, label_div)
                else:
                    value_div = MyHTML.div('my_waves_{}_{}_value_div'.format(row_number, column_number), index, True)
                    self.set_value(row_number, column_number, value_div)

    @staticmethod
    def __get_table_header_dict__():
        return {WAVEST.INDICES: 'Indices',
                WAVEST.INTRADAY_ASC: 'Intraday (ascending)',
                WAVEST.INTRADAY_DESC: 'Intraday (descending)',
                WAVEST.DAILY_ASC: 'Daily (ascending)',
                WAVEST.DAILY_DESC: 'Daily (descending)'}

    def _get_cell_style_(self, row: int, col: int):
        base_width = int(100/self._column_number)
        width_list = ['{}%'.format(base_width) for k in range(0, self._column_number)]
        width = width_list[col - 1]
        bg_color = COLORS[2]['background'] if row == 1 or col == 1 else COLORS[1]['background']
        color = COLORS[2]['text']
        text_align = 'left' if col == 1 else 'center'
        v_align = 'top'
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}


class MyHTMLTabTradeHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        ticker_label_div = MyHTML.div('my_trade_ticker_label_div', 'Ticker:', True)
        ticker_div = MyHTML.div('my_trade_ticker_div', '', False)

        self.set_value(1, 1, MyHTML.div_embedded([ticker_label_div, MyHTML.span(' '), ticker_div]))
        self.set_value(1, 2, MyDCC.markdown('my_trade_markdown'))
        self.set_value(1, 3, MyDCC.markdown('my_trade_news_markdown'))


class MyHTMLTabTradeStatisticsHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        chart_label_div = MyHTML.div('my_trade_statistics_chart_type_label_div', 'Chart:', True)
        chart_div = MyHTML.div('my_trade_statistics_chart_type_div', '', False)

        statistics_label_div = MyHTML.div('my_trade_statistics_label_div', 'Trades:', True)
        statistics_div = MyHTML.div('my_trade_statistics_div', '0 (+0/-0)')
        statistics_summary_div = MyHTML.div_embedded([statistics_label_div, MyHTML.span(' '), statistics_div])

        my_trades_number_label_div = MyHTML.div('my_trades_number_label_div', 'Trades (R/S):', True)
        my_trades_number_div = MyHTML.div('my_trades_number_div', '0/0 0/0')
        my_trades_number_summary_div = MyHTML.div_embedded(
            [my_trades_number_label_div, MyHTML.span(' '), my_trades_number_div])

        my_trades_mean_label_div = MyHTML.div('my_trades_mean_label_div', '...(mean %):', True)
        my_trades_mean_div = MyHTML.div('my_trades_mean_div', '0/0 0/0')
        my_trades_mean_summary_div = MyHTML.div_embedded(
            [my_trades_mean_label_div, MyHTML.span(' '), my_trades_mean_div])

        self.set_value(1, 1, MyHTML.div_embedded([chart_label_div, MyHTML.span(' '), chart_div]))
        self.set_value(1, 2, MyDCC.markdown('my_trade_statistics_markdown'))
        self.set_value(1, 3, MyHTML.div_embedded([statistics_summary_div, my_trades_number_summary_div,
                                                 my_trades_mean_summary_div]))


class MyHTMLTabAssetStatisticsHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        crypto_client_label_div = MyHTML.div('my_asset_crypto_client_label_div', 'Bitfinex:', bold=True)
        crypto_client_value_div = MyHTML.div('my_asset_crypto_client_div', '0', bold=False)
        crypto_client_div = MyHTML.div_embedded([crypto_client_label_div, MyHTML.span(' '), crypto_client_value_div])

        stock_client_label_div = MyHTML.div('my_asset_stock_client_label_div', 'IKBR:', bold=True)
        stock_client_value_div = MyHTML.div('my_asset_stock_client_div', '0', bold=False)
        stock_client_div = MyHTML.div_embedded([stock_client_label_div, MyHTML.span(' '), stock_client_value_div])

        crypto_client_trades_label_div = MyHTML.div('my_asset_crypto_client_trades_label_div',
                                                    'Trades (Bitfinex):', bold=True)
        crypto_client_trades_value_div = MyHTML.div('my_asset_crypto_client_trades_div', '0', bold=False)
        crypto_client_trades_div = MyHTML.div_embedded([
            crypto_client_trades_label_div, MyHTML.span(' '), crypto_client_trades_value_div])

        stock_client_trades_label_div = MyHTML.div('my_asset_stock_client_trades_label_div',
                                                    'Trades (IBKR):', bold=True)
        stock_client_trades_value_div = MyHTML.div('my_asset_stock_client_trades_div', '0', bold=False)
        stock_client_trades_div = MyHTML.div_embedded([
            stock_client_trades_label_div, MyHTML.span(' '), stock_client_trades_value_div])

        self.set_value(1, 1, MyHTML.div_embedded([crypto_client_div, stock_client_div]))
        self.set_value(1, 2, MyDCC.markdown('my_asset_statistics_markdown'))
        self.set_value(1, 3, MyHTML.div_embedded([crypto_client_trades_div, stock_client_trades_div]))


class MyHTMLTabModelsStatisticsHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        crypto_client_label_div = MyHTML.div('my_models_crypto_client_label_div', 'Bitfinex:', bold=True)
        crypto_client_value_div = MyHTML.div('my_models_crypto_client_div', '0', bold=False)
        crypto_client_div = MyHTML.div_embedded([crypto_client_label_div, MyHTML.span(' '), crypto_client_value_div])

        stock_client_label_div = MyHTML.div('my_models_stock_client_label_div', 'IKBR:', bold=True)
        stock_client_value_div = MyHTML.div('my_models_stock_client_div', '0', bold=False)
        stock_client_div = MyHTML.div_embedded([stock_client_label_div, MyHTML.span(' '), stock_client_value_div])

        crypto_client_trades_label_div = MyHTML.div('my_models_crypto_client_trades_label_div',
                                                    'Trades (Bitfinex):', bold=True)
        crypto_client_trades_value_div = MyHTML.div('my_models_crypto_client_trades_div', '0', bold=False)
        crypto_client_trades_div = MyHTML.div_embedded([
            crypto_client_trades_label_div, MyHTML.span(' '), crypto_client_trades_value_div])

        stock_client_trades_label_div = MyHTML.div('my_models_stock_client_trades_label_div',
                                                    'Trades (IBKR):', bold=True)
        stock_client_trades_value_div = MyHTML.div('my_models_stock_client_trades_div', '0', bold=False)
        stock_client_trades_div = MyHTML.div_embedded([
            stock_client_trades_label_div, MyHTML.span(' '), stock_client_trades_value_div])

        self.set_value(1, 1, MyHTML.div_embedded([crypto_client_div, stock_client_div]))
        self.set_value(1, 2, MyDCC.markdown('my_models_statistics_markdown'))
        self.set_value(1, 3, MyHTML.div_embedded([crypto_client_trades_div, stock_client_trades_div]))


class MyHTMLTabPatternStatisticsHeaderTable(MyHTMLTabHeaderTable):
    def _init_cells_(self):
        chart_label_div = MyHTML.div('my_pattern_statistics_chart_label_div', 'Chart:', True)
        chart_div = MyHTML.div('my_pattern_statistics_chart_type_div', '', False)
        statistics_label_div = MyHTML.div('my_pattern_statistics_label_div', 'Pattern:', True)
        statistics_div = MyHTML.div('my_pattern_statistics_div', '0')
        statistics_summary_div = MyHTML.div_embedded([statistics_label_div, MyHTML.span(' '), statistics_div])
        statistics_detail_label_div = MyHTML.div('my_pattern_statistics_detail_label_div', 'Type:', True)
        statistics_detail_div = MyHTML.div('my_pattern_statistics_detail_div', '0')
        statistics_detail_summary_div = MyHTML.div_embedded([statistics_detail_label_div, MyHTML.span(' '),
                                                             statistics_detail_div])
        self.set_value(1, 1, MyHTML.div_embedded([chart_label_div, MyHTML.span(' '), chart_div]))
        self.set_value(1, 2, MyDCC.markdown('my_pattern_statistics_markdown'))
        self.set_value(1, 3, MyHTML.div_embedded([statistics_summary_div, statistics_detail_summary_div]))



