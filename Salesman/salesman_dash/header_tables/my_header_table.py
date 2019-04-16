"""
Description: This module contains the html header table for the dash application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from datetime import datetime
from sertl_analytics.mydates import MyDate
from sertl_analytics.mydash.my_dash_components import MyHTMLTable, COLORS, MyHTML, MyDCC


class MyHTMLHeaderTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 2, 3)

    def _init_cells_(self):
        user_label_div = MyHTML.div('my_user_label_div', 'Username:', True)
        user_div = MyHTML.div('my_user_name_div', 'Josef Sertl', False)
        time_str = MyDate.get_time_from_datetime(datetime.now())
        login_label_div = MyHTML.div('my_login_label_div', 'Last login:', True, True)
        login_time_div = MyHTML.div('my_login_div', '{}'.format(time_str), False)
        sound_label_div = MyHTML.div('my_sound_label_div', 'Sound:', True, True)
        sound_div = MyHTML.div('my_sound_div', '', False)
        mode_label_div = MyHTML.div('my_mode_label_div', 'Mode:', True, True)
        mode_div = MyHTML.div('my_mode_div', '', False)
        max_buy_label_div = MyHTML.div('my_max_buy_label_div', 'Max buy value:', True, True)
        max_buy_div = MyHTML.div('my_max_buy_div', '', False)
        small_profit_label_div = MyHTML.div('my_small_profit_label_div', 'Small profit taking:', True, True)
        small_profit_div = MyHTML.div('my_small_profit_div', '', False)

        my_user_div = MyHTML.div_embedded([user_label_div, MyHTML.span(' '), user_div])
        my_login_div = MyHTML.div_embedded([login_label_div, MyHTML.span(' '), login_time_div])
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
        self.set_value(1, 3, MyHTML.div_embedded([time_div, next_refresh_div, last_refresh_div]))
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

