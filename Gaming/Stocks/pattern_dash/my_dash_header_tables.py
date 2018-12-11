"""
Description: This module contains the html header tables for the dash application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from datetime import datetime
from sertl_analytics.mydates import MyDate
from pattern_dash.my_dash_components import MyHTMLTable, COLORS, MyHTML, MyDCC


class MyHTMLHeaderTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 2, 3)

    def _init_cells_(self):
        user_label_div = MyHTML.div('my_user_label_div', 'Username:', True)
        user_div = MyHTML.div('my_user_name_div', 'Josef Sertl', False)
        time_str = MyDate.get_time_from_datetime(datetime.now())
        login_label_div = MyHTML.div('my_login_label_div', 'Last login:', True, True)
        login_time_div = MyHTML.div('my_login_div', '{}'.format(time_str), False)
        my_user_div = MyHTML.div_embedded([user_label_div, MyHTML.span(' '), user_div])
        my_login_div = MyHTML.div_embedded([login_label_div, MyHTML.span(' '), login_time_div])

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

        online_trade_label_div = MyHTML.div('my_online_trade_label_div', 'Trades - Online:', True)
        online_trade_active_div = MyHTML.div('my_online_trade_active_div', '0')
        online_trade_all_div = MyHTML.div('my_online_trade_all_div', '0')
        stored_trade_label_div = MyHTML.div('my_stored_trade_label_div', 'Trades - Replay:', True)
        stored_trade_div = MyHTML.div('my_stored_trade_div', '0')
        stored_pattern_label_div = MyHTML.div('my_stored_pattern_label_div', 'Pattern - Replay:', True)
        stored_pattern_div = MyHTML.div('my_stored_pattern_div', '0')
        online_div = MyHTML.div_embedded([
            online_trade_label_div, MyHTML.span(' '),
            online_trade_active_div, MyHTML.span('/'), online_trade_all_div], inline=True)
        trade_div = MyHTML.div_embedded([stored_trade_label_div, MyHTML.span(' '), stored_trade_div])
        pattern_div = MyHTML.div_embedded([stored_pattern_label_div, MyHTML.span(' '), stored_pattern_div])

        self.set_value(1, 1, MyHTML.div_embedded([my_user_div, my_login_div]))
        self.set_value(1, 2, MyHTML.div_embedded([dash_board_title_div, dash_board_sub_title_div]))
        self.set_value(1, 3, MyHTML.div_embedded([time_div, next_refresh_div, last_refresh_div]))
        self.set_value(2, 1, MyDCC.markdown('my_position_markdown'))
        self.set_value(2, 2, MyDCC.markdown('my_dashboard_markdown'))
        self.set_value(2, 3, MyHTML.div_embedded([online_div, trade_div, pattern_div]))

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
        statistics_detail_label_div = MyHTML.div('my_trade_statistics_detail_label_div', 'Type:', True)
        statistics_detail_div = MyHTML.div('my_trade_statistics_detail_div', '0')
        statistics_detail_summary_div = MyHTML.div_embedded([statistics_detail_label_div, MyHTML.span(' '),
                                                             statistics_detail_div])
        self.set_value(1, 1, MyHTML.div_embedded([chart_label_div, MyHTML.span(' '), chart_div]))
        self.set_value(1, 2, MyDCC.markdown('my_trade_statistics_markdown'))
        self.set_value(1, 3, MyHTML.div_embedded([statistics_summary_div, statistics_detail_summary_div]))


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



