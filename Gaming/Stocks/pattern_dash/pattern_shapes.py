"""
Description: This module contains all shapes which are used for pattern dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


import datetime as dt


class MyShape:
    def __init__(self, x: list, y: list):
        self.x = x
        self.y = y
        self._visible = True

    @property
    def shape_parameters(self):
        return self.__get_shape_parameter_dict__()

    @property
    def annotation_parameters(self):
        return self.__get_annotation_parameter_dict__()

    def __get_svg_path__(self):
        length = len(self.x)
        svg_path = ''
        for k in range(0, length):
            if k == 0:
                svg_path = 'M {},{}'.format(self.x[k], self.y[k])
            elif k == length - 1:
                svg_path += ' Z'
            else:
                svg_path += ' L {},{}'.format(self.x[k], self.y[k])
        return svg_path

    def __get_shape_parameter_dict__(self) -> dict:
        pass

    def __get_annotation_parameter_dict__(self) -> dict:
        pass


class MyLineShape(MyShape):
    def __get_shape_parameter_dict__(self) -> dict:
        return {'type': 'line', 'visible': self._visible, 'line': {'color': 'k', 'width': 1},
                'x0': self.x[0], 'x1': self.x[1], 'y0': self.y[0], 'y1': self.y[1]}


class MyPolygonShape(MyShape):
    def __get_shape_parameter_dict__(self) -> dict:
        return {'type': 'path', 'visible': self._visible,
                'path': self.__get_svg_path__(), 'line': {'color': 'red', 'width': 1},
                'fillcolor': 'red', 'opacity': 0.3}

    def __get_annotation_parameter_dict__(self) -> dict:
        return {'x': self.x[0], 'y': self.y[0],
                'showarrow': False, 'xanchor': 'left',
                'text': 'Increase Period Begins'}


class MyCircleShape(MyShape):
    def __init__(self, x_center: float, y_center: float, radius: float):
        self.radius = radius
        MyShape.__init__(self, [x_center], [y_center])

    def __get_shape_parameter_dict__(self) -> dict:
        date_value = dt.datetime.strptime(self.x[0], '%Y-%m-%d')
        date_value = date_value + dt.timedelta(days=1)
        return {'type': 'circle', 'visible': self._visible, 'xref': 'x', 'yref': 'y',
                'x0': self.x[0], 'x1': date_value.strftime("%Y-%m-%d"),
                'y0': self.y[0], 'y1': self.y[0] + self.radius,
                'fillcolor': 'yellow',
                'line': {'color': 'yellow', 'width': 1}}