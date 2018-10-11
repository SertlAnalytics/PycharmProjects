"""
Description: This module contains some tools for MyDash - like caching.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


from playsound import playsound
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mycache import MyCache, MyCacheObject, MyCacheObjectApi
from copy import deepcopy


class MyGraphCacheObjectApi(MyCacheObjectApi):
    def __init__(self, sys_config: SystemConfiguration):
        MyCacheObjectApi.__init__(self)
        self.sys_config = sys_config
        self.detector = None
        self.pattern_data = None
        self.last_refresh_ts = None
        self.period_aggregation_ts = self.sys_config.config.api_period_aggregation * 60


class MyGraphCacheObject(MyCacheObject):
    def __init__(self, cache_api: MyGraphCacheObjectApi):
        MyCacheObject.__init__(self, cache_api)
        self.sys_config = cache_api.sys_config
        self.detector = cache_api.detector
        self.pattern_data = cache_api.pattern_data
        self.last_refresh_ts = cache_api.last_refresh_ts
        self.period_aggregation_ts = self.sys_config.config.api_period_aggregation * 60
        self.adjusted_last_refresh_ts = \
            self.sys_config.config.get_time_stamp_before_one_period_aggregation(self.last_refresh_ts)
        self.cached_before_breakout = self.__was_cached_before_breakout__()
        self.breakout_since_last_data_update = self.__was_breakout_since_last_data_update__()
        self.fibonacci_finished_since_last_data_update = self.__was_fibonacci_finished_since_last_data_update__()
        self.touch_since_last_data_update = self.__was_any_touch_since_last_data_update__()

    def is_under_observation(self):
        return self.cached_before_breakout or self.breakout_since_last_data_update or \
               self.fibonacci_finished_since_last_data_update

    def __was_any_touch_since_last_data_update__(self):
        return self.detector.was_any_touch_since_time_stamp(self.adjusted_last_refresh_ts, True)

    def __was_breakout_since_last_data_update__(self):
        return self.detector.was_any_breakout_since_time_stamp(self.adjusted_last_refresh_ts, self.id, True)

    def __was_fibonacci_finished_since_last_data_update__(self):
        return self.detector.fib_wave_tree.was_any_wave_finished_since_time_stamp(self.adjusted_last_refresh_ts)

    def __was_cached_before_breakout__(self) -> bool:
        return self.detector.is_any_pattern_without_breakout()


class MyGraphCache(MyCache):
    def __init__(self):
        MyCache.__init__(self)
        self.__cached_and_under_observation_play_sound_list = []

    @property
    def number_of_finished_fibonacci_waves_since_last_refresh(self) -> int:
        number_return = 0
        for cache_object in self._cached_object_dict.values():
            if cache_object.fibonacci_finished_since_last_data_update:
                number_return += 1
        return number_return

    @staticmethod
    def get_cache_key(graph_id: str, ticker: str, days: int = 0):
        return '{}_{}_{}'.format(graph_id, ticker, days)

    def add_cache_object(self, cache_api: MyGraphCacheObjectApi):
        self._cached_object_dict[cache_api.key] = MyGraphCacheObject(cache_api)
        self._cached_object_dict[cache_api.key].print()

    def get_detector(self, cache_key: str):
        return self._cached_object_dict[cache_key].detector

    def get_pattern_data(self, cache_key):
        return self._cached_object_dict[cache_key].pattern_data

    def was_breakout_since_last_data_update(self, cache_key: str):
        if cache_key in self._cached_object_dict:
            return self._cached_object_dict[cache_key].breakout_since_last_data_update
        return False

    def was_touch_since_last_data_update(self, cache_key: str):
        if cache_key in self._cached_object_dict:
            return self._cached_object_dict[cache_key].touch_since_last_data_update
        return False

    def get_graph_list_for_observation(self, key_not: str) -> list:
        play_sound = False
        graphs = []
        for key, cache_object in self._cached_object_dict.items():
            if key != key_not and cache_object.is_under_observation():
                if key not in self.__cached_and_under_observation_play_sound_list:
                    self.__cached_and_under_observation_play_sound_list.append(key)
                    play_sound = True
                graphs.append(self.__change_to_observation_graph__(cache_object.object, len(graphs)))
            elif not cache_object.is_under_observation():
                if key in self.__cached_and_under_observation_play_sound_list:
                    self.__cached_and_under_observation_play_sound_list.remove(key)
        if play_sound:
            playsound('ring08.wav')  # C:/Windows/media/...
        return graphs

    def get_pattern_list_for_buy_trigger(self, buy_trigger: str) -> list:
        pattern_list = []
        for key, cache_object in self._cached_object_dict.items():
            if cache_object.is_under_observation():
                pattern_list += cache_object.detector.get_pattern_list_for_buy_trigger(buy_trigger)
        return pattern_list

    @staticmethod
    def __change_to_observation_graph__(graph_old, number: int):
        graph = deepcopy(graph_old)
        graph.id = 'my_new_key_{}'.format(number)
        graph.figure['layout']['height'] = graph.figure['layout']['height'] # /2
        return graph


class MyDashStateHandler:
    def __init__(self, ticker_list: list):
        self._my_refresh_button_clicks = 0
        self._my_interval_n_intervals = 0
        self._my_interval_selection = 0
        self._ticker_dict = {dict_element['value']: 0 for dict_element in ticker_list}

    def change_for_my_interval_selection(self, interval_selection: int) -> bool:
        if interval_selection != self._my_interval_selection:
            self._my_interval_selection = interval_selection
            return True
        return False

    def change_for_my_refresh_button(self, n_clicks: int) -> bool:
        if n_clicks > self._my_refresh_button_clicks:
            self._my_refresh_button_clicks = n_clicks
            return True
        return False

    def change_for_my_interval(self, n_intervals: int) -> bool:
        if n_intervals > self._my_interval_n_intervals:
            self._my_interval_n_intervals = n_intervals
            return True
        return False

    def add_selected_ticker(self, ticker: str):
        if ticker in self._ticker_dict:
            self._ticker_dict[ticker] += 1

    def get_next_most_selected_ticker(self, ticker_selected: str):
        max_count = 0
        max_ticker = ''
        for key, number in self._ticker_dict.items():
            if key != ticker_selected and number > max_count:
                max_ticker = key
                max_count = number
        return max_ticker

