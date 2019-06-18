"""
Description: This module contains file handler classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-06-14
"""


class MyFile:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._line_numbers = self.__get_line_number_for_file__()

    @property
    def line_numbers(self) -> int:
        return self._line_numbers

    def get_lines_as_list(self) -> list:
        lines = []
        with open(self._file_path, 'r') as file:
            for line in file.readlines():
                lines.append(line)
        return lines

    def replace_file_when_changed(self, lines_new: list):
        if self._line_numbers > len(lines_new):
            print('Update file: {}, old: {}, new={} lines'.format(self._file_path, self._line_numbers, len(lines_new)))
            with open(self._file_path, 'w') as file:
                for line in lines_new:
                    file.write(line)

    def __get_line_number_for_file__(self):
        num_lines = 0
        with open(self._file_path) as file:
            num_lines += sum(1 for line in file)
        return num_lines


