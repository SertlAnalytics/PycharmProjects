"""
Description: This module contains the sound module for the application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Original sounds: # C:/Windows/media/...
Date: 2018-06-17
"""

from playsound import playsound


class PatternSoundMachine:
    is_active = True

    def play_alarm_buy(self):
        self.__play__('alarm_buy.wav')

    def play_alarm_after_sell(self, trade_result_pct: float):
        self.play_alarm_sell_ok() if trade_result_pct > 0 else self.play_alarm_sell_nok()

    def play_alarm_sell_ok(self):
        self.__play__('alarm_sell_ok.wav')

    def play_alarm_sell_nok(self):
        self.__play__('alarm_sell_nok.wav')

    def play_alarm_new_pattern(self):
        self.__play__('alarm_new_pattern.wav')

    def play_alarm_fibonacci(self):
        self.__play__('alarm_fibonacci.wav')

    def play_alarm_bollinger_band_break(self):
        self.__play__('alarm_fibonacci.wav')

    def play_alarm_touch_point(self):
        self.__play__('alarm_touchpoint.wav')

    def __play__(self, file: str):
        if self.is_active:
            try:
                directory = '../pattern_sound/'
                playsound('{}{}'.format(directory, file))
            except:
                directory = 'pattern_sound/'
                playsound('{}{}'.format(directory, file))
            finally:
                pass

