"""
Description: This module contains the html configuration tables for the dash application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-09
"""

from pattern_dash.my_dash_components import MyHTMLTable, COLORS, MyHTML
from pattern_system_configuration import SystemConfiguration
from pattern_configuration import PatternConfiguration
from pattern_runtime_configuration import RuntimeConfiguration
from pattern_bitfinex import BitfinexConfiguration
from pattern_trade_optimizer import TradeOptimizer


class MyHTMLConfigurationTable(MyHTMLTable):
    def __init__(self, config: object):
        self.config = config
        self.config_name = self.config.__class__.__name__
        self.properties = []
        self.value_dict = {}
        self.__init_by_class_properties__()
        self.__add_class_specific_entries__()
        MyHTMLTable.__init__(self, len(self.properties) + 1, 3, self.config_name)

    @property
    def div_id(self):
        return 'my_table_{}_div'.format(self.config_name.lower())

    def get_table_as_div(self):
        return MyHTML.div(self.div_id, [self.get_table()])

    def _init_cells_(self):
        self.set_value(1, 1, 'Property')
        self.set_value(1, 2, 'Value')
        self.set_value(1, 3, 'Comment')
        row = 1
        for prop in sorted(self.properties):
            row += 1
            self.set_value(row, 1, prop)
            self.set_value(row, 2, '{}'.format(self.value_dict[prop]))
            self.set_value(row, 3, '')

    def __init_by_class_properties__(self):
        for key, value in self.config.__dict__.items():
            self.__add_key_value_pair__(key, value)

    def __add_class_specific_entries__(self):
        pass

    def __add_key_value_pair__(self, key: str, value: object):
        if type(value) in [str, bool, float, int, list, dict]:
            if key.find(self.config_name) < 0 and key[0] != '_':  # we don't want to have private properties
                self.properties.append(key)
                self.value_dict[key] = value

    def _get_cell_style_(self, row: int, col: int):
        width = ['20%', '40%', '40%'][col - 1]
        bg_color = COLORS[1]['background'] if row == 1 else COLORS[0]['background']
        color = COLORS[2]['text']
        text_align = 'center' if row == 1 else 'left'
        v_align = 'top'
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}


class MyHTMLSystemConfigurationTable(MyHTMLConfigurationTable):
    def __init__(self, config: SystemConfiguration):
        self.config = config
        MyHTMLConfigurationTable.__init__(self, config)

    def __add_class_specific_entries__(self):
        self.__add_key_value_pair__('expected_win_pct', self.config.expected_win_pct)
        self.__add_key_value_pair__('value_categorizer_tolerance_pct',
                                    self.config.get_value_categorizer_tolerance_pct())
        self.__add_key_value_pair__('value_categorizer_tolerance_pct_equal',
                                    self.config.get_value_categorizer_tolerance_pct_equal())
        self.__add_key_value_pair__('ticker_dict', self.config.ticker_dict)
        self.__add_key_value_pair__('from_db', self.config.from_db)
        self.__add_key_value_pair__('period', self.config.period)
        self.__add_key_value_pair__('period_aggregation', self.config.period_aggregation)
        self.__add_key_value_pair__('sound_machine.is_active', self.config.sound_machine.is_active)


class MyHTMLPatternConfigurationTable(MyHTMLConfigurationTable):
    def __init__(self, config: PatternConfiguration):
        self.config = config
        MyHTMLConfigurationTable.__init__(self, config)

    def __add_class_specific_entries__(self):
        self.__add_key_value_pair__('previous_period_length', self.config.previous_period_length)


class MyHTMLRuntimeConfigurationTable(MyHTMLConfigurationTable):
    def __init__(self, config: RuntimeConfiguration):
        self.config = config
        MyHTMLConfigurationTable.__init__(self, config)

    def __add_class_specific_entries__(self):
        pass


class MyHTMLBitfinexConfigurationTable(MyHTMLConfigurationTable):
    def __init__(self, config: BitfinexConfiguration):
        self.config = config
        MyHTMLConfigurationTable.__init__(self, config)

    def __add_class_specific_entries__(self):
        pass


class MyHTMLTradeOptimizerTable(MyHTMLConfigurationTable):
    def __init__(self, config: TradeOptimizer):
        self.config = config
        MyHTMLConfigurationTable.__init__(self, config)

    def __add_class_specific_entries__(self):
        self.__add_key_value_pair__('pattern_type_pos_neg_result_dict', self.config.pattern_type_pos_neg_result_dict)
        self.__add_key_value_pair__('optimal_pattern_type_dict_for_long_trading',
                                    self.config.optimal_pattern_type_dict_for_long_trading)



