import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle, Arrow, Ellipse


class MyPlotHelper:
    @staticmethod
    def get_polygon_for_tick_list(tick_list: list, func, closed: bool = True):
        x = [tick.date_num for tick in tick_list]
        y = [func(tick.position) for tick in tick_list]
        xy = list(zip(x, y))
        return Polygon(np.array(xy), closed=closed)

    @staticmethod
    def get_xy_parameter_for_tick_function_list(tick_list: list, func_list, closed: bool = True):
        x = [tick.date_num for tick in tick_list]
        y = [func(tick_list[ind].position) for ind, func in enumerate(func_list)]
        return list(zip(x, y))
