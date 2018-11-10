"""
Description: This job updates the trade records for all pattern without that trade type.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.constants.pattern_constants import BT, TSTR, FT, DC, PRD, TRT
from pattern_system_configuration import SystemConfiguration
from pattern_detection_controller import PatternDetectionController

sys_config = SystemConfiguration()
sys_config.init_detection_process_for_automated_trade_update(16)
trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.LIMIT_FIX, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP]}
# sys_config.config.pattern_type_list = [FT.TRIANGLE]
for pattern_type in FT.get_long_trade_able_types():
    where_clause = "pattern_type = '{}' and period = 'DAILY' and trade_type in ('', 'longxxx')".format(pattern_type)
    df_pattern_for_pattern_type = sys_config.db_stock.get_pattern_records_as_dataframe(where_clause)
    pattern_id_dict = {row[DC.ID]: row[DC.TRADE_TYPE] for index, row in df_pattern_for_pattern_type.iterrows()}
    # pattern_id_list = ['20_1_1_LTCUSD_20_2016-11-02_00:00_2016-12-04_00:00']
    counter = 0
    for pattern_id, trade_type in pattern_id_dict.items():
        counter += 1
        run_detail = '{} ({:03d} of {:03d}): {}'.format(pattern_type, counter, len(pattern_id_dict), pattern_id)
        result_dict = sys_config.db_stock.get_missing_trade_strategies_for_pattern_id(pattern_id, trade_strategy_dict)
        for buy_trigger, trade_strategy_list in result_dict.items():
            if len(trade_strategy_list) == 0:
                print('{}: OK'.format(run_detail))
            else:
                print('{}: processing...'.format(run_detail))
                sys_config.config.pattern_ids_to_find = [pattern_id]
                sys_config.exchange_config.trade_strategy_dict = {buy_trigger: trade_strategy_list}
                pattern_controller = PatternDetectionController(sys_config)
                pattern_controller.run_pattern_detector()
        if trade_type == '':
            sys_config.db_stock.update_trade_type_for_pattern(pattern_id, TRT.LONG)





