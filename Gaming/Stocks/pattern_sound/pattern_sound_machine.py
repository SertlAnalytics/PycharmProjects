"""
Description: This module contains the sound module for the application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Original sounds: # C:/Windows/media/...
Date: 2018-06-17
"""

from playsound import playsound


class PatternSoundMachine:
    def __init__(self):
        self._is_active = True

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value

    def play_alarm_buy(self):
        self.__play__('alarm_buy.wav')

    def play_alarm_sell_ok(self):
        self.__play__('alarm_sell_ok.wav')

    def play_alarm_sell_nok(self):
        self.__play__('alarm_sell_nok.wav')

    def play_alarm_new_pattern(self):
        self.__play__('alarm_new_pattern.wav')

    def play_alarm_fibonacci(self):
        self.__play__('alarm_fibonacci.wav')

    def play_alarm_touch_point(self):
        self.__play__('alarm_touchpoint.wav')

    def __play__(self, file: str):
        if self._is_active:
            playsound('{}{}'.format('pattern_sound/', file))