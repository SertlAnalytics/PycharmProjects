"""
Description: This module contains the PatternDataMatrix which is used for correct presentation of the annotation text
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-17
"""

from pattern_data_container import PatternData


class PatternDataCell:
    def __init__(self, row: int, column: int, left_bottom_coordinates: tuple, height: float, width: int):
        self._row = row
        self._col = column
        self._height = height
        self._width = width
        self._x_left = left_bottom_coordinates[0]
        self._x_right = self._x_left + width
        self._y_min = left_bottom_coordinates[1]
        self._y_max = self._y_min + height

    def get_row_column_numbers(self) -> tuple:
        return self._row, self._col

    def is_value_in_cell(self, x: int, y: float) -> bool:
        if self._x_left <= x < self._x_right:
            return self._y_min <= y < self._y_max
        return False

    def get_center_coordinates(self):
        x = int(self._x_left + self._width/2)
        y = self._y_min + self._height/2
        return [x, y]

    def get_left_top_coordinates(self):
        return self._x_left, self._y_max

    def get_left_bottom_coordinates(self):
        return self._x_left, self._y_min


class PatternDataMatrix:
    def __init__(self, pattern_data: PatternData, row_number=3, column_number=3):
        self._row_number = row_number
        self._column_number = column_number
        self._pattern_data = pattern_data
        self._y_min = self._pattern_data.min_value
        self._y_max = self._pattern_data.max_value
        self._x_start = self._pattern_data.tick_first.time_stamp
        self._x_end = self._pattern_data.tick_last.time_stamp
        self._cell_height = (self._y_max - self._y_min)/self._row_number
        self._cell_width = int((self._x_end - self._x_start)/self._column_number)
        self._matrix = self.__get_matrix__()

    def get_x_y_off_set_for_shape_annotation(self, center_xy: tuple) -> list:
        cell_with_value = self.__get_cell_for_values__(center_xy)
        if cell_with_value is None:
            return [0, 0]
        row_number, column_number = cell_with_value.get_row_column_numbers()
        cell_for_text = self.__get_cell_with_text__(column_number, row_number)
        x, y = cell_for_text.get_left_bottom_coordinates()
        return [x - center_xy[0], y - center_xy[1]]

    def __get_cell_with_text__(self, column_number: int, row_number: int):
        """
        We have to find the cell which have enough space for the text within the whole grid
        """
        row_adjust = - 1 if row_number == self._row_number else 1
        column_adjust = 0 if column_number == 1 else -1
        return self.__get_cell__(row_number + row_adjust, column_number + column_adjust)

    def __get_cell__(self, row: int, col: int):
        return self._matrix[row-1][col-1]

    def __get_cell_for_values__(self, xy_values: tuple):
        for r in range(0, self._row_number):
            for col in range(0, self._column_number):
                cell = self._matrix[r][col]
                if cell.is_value_in_cell(xy_values[0], xy_values[1]):
                    return cell

    def __get_matrix__(self):
        matrix = []
        y = self._y_min
        for r in range(0, self._row_number):
            x = self._x_start
            row = []
            for col in range(0, self._column_number):
                row.append(PatternDataCell(r+1, col+1, (x, y), self._cell_height, self._cell_width))
                x += self._cell_width
            matrix.append(row)
            y += self._cell_height
        return matrix

