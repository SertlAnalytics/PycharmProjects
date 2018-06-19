"""
Description: This module contains different functions for Bokeh.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""

import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.io import output_file, show, save
from bokeh.sampledata.stocks import AAPL, GOOG, IBM, MSFT
from bokeh.sampledata.iris import flowers
from math import pi
from bokeh.models import HoverTool, ResetTool, PanTool, WheelPanTool, WheelZoomTool, SaveTool, ColumnDataSource
from bokeh.sampledata.periodic_table import elements
from bokeh.models.annotations import Span, BoxAnnotation, Label, LabelSet


class FT:  # figure types
    CIRCLE = 'Circle'
    LINE = 'Line'
    TRIANGLE = 'Triangle'


class MyBokehClass:
    def __init__(self):
        self.f = figure()

    def __show__(self, with_save = False):
        if with_save:
            save(self.f)
        show(self.f)

    def show_elements(self):
        elements.dropna(inplace=True)  # if inplace is not set to True the changes are not written to the dataframe
        colormap = {'gas': 'yellow', 'liquid': 'orange', 'solid': 'red'}
        elements['color'] = [colormap[x] for x in elements['standard state']]
        elements['size'] = elements["van der Waals radius"] / 10

        # Create three ColumnDataSources for elements of unique standard states
        gas = ColumnDataSource(elements[elements['standard state'] == 'gas'])
        liquid = ColumnDataSource(elements[elements['standard state'] == 'liquid'])
        solid = ColumnDataSource(elements[elements['standard state'] == 'solid'])

        # Define the output file path
        output_file("elements.html")

        # adding glyphs
        self.f.circle(x="atomic radius", y="boiling point", size='size', fill_alpha=0.2, color="color",
                 legend='Gas', source=gas)

        self.f.circle(x="atomic radius", y="boiling point", size='size', fill_alpha=0.2, color="color",
                 legend='Liquid', source=liquid)

        self.f.circle(x="atomic radius", y="boiling point", size='size', fill_alpha=0.2, color="color",
                 legend='Solid', source=solid)

        self.f.xaxis.axis_label = "Atomic radius"
        self.f.yaxis.axis_label = "Boiling point"

        # Save and show the figure
        self.__show__()

    def show_iris(self):
        output_file("iris.html")
        # self.f.circle(x=flowers["petal_length"], y=flowers["petal_width"])
        # hover = HoverTool(tooltips=[("Species", "@species"), ("Sepal Width", "@sepal_width")])
        hover = self.__get_hover_with_style__()

        # Style the tools
        self.f.tools = [PanTool(), ResetTool()]
        self.f.add_tools(hover)  # overwrites the default self.f.add_tools(Hovertools()) - but without details...
        # WE NEED a ColumnDataSource - Not a pd.DataFrame or others...
        self.f.toolbar_location = 'above'
        self.f.toolbar.logo = None

        # Style the plot area
        self.f.plot_width = 1100
        self.f.plot_height = 650
        self.f.background_fill_color = "olive"
        self.f.background_fill_alpha = 0.3

        # Style the title
        self.f.title.text = "Iris Morphology"
        self.f.title.text_color = "olive"
        self.f.title.text_font = "times"
        self.f.title.text_font_size = "25px"
        self.f.title.align = "center"

        # Style the axes
        self.f.xaxis.minor_tick_line_color = "blue"
        self.f.yaxis.major_label_orientation = "vertical"
        self.f.xaxis.visible = True
        self.f.xaxis.minor_tick_in = -6
        self.f.xaxis.axis_label = "Petal Length"
        self.f.yaxis.axis_label = "Petal Width"
        self.f.axis.axis_label_text_color = "blue"
        self.f.axis.major_label_text_color = "orange"

        # # Axes geometry
        # self.f.x_range = Range1d(start=0, end=10)
        # self.f.y_range = Range1d(start=0, end=5)
        # self.f.xaxis.bounds = (2, 6)
        # self.f.xaxis[0].ticker.desired_num_ticks = 2
        # self.f.yaxis[0].ticker.desired_num_ticks = 2
        # self.f.yaxis[0].ticker.num_minor_ticks = 10

        # Style the grid
        # self.f.xgrid.grid_line_color = None
        # self.f.ygrid.grid_line_alpha = 0.6
        # self.f.grid.grid_line_dash = [5, 3]

        colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
        flowers['color'] = [colormap[x] for x in flowers['species']]

        # adding glyphs
        self.__add_glyphs__(True)

        # Style the legend
        # self.f.legend.location = (575, 555)
        self.f.legend.location = 'top_left'
        self.f.legend.background_fill_alpha = 0
        self.f.legend.border_line_color = None
        self.f.legend.margin = 10
        self.f.legend.padding = 18
        self.f.legend.label_text_color = 'olive'
        self.f.legend.label_text_font = 'times'

        self.__show__()

    @staticmethod
    def __get_hover_with_style__():
        return HoverTool(tooltips="""
             <div>
                    <div>
                        <img
                            src="@imgs" height="42" alt="@imgs" width="42"
                            style="float: left; margin: 0px 15px 15px 0px;"
                            border="2"
                        ></img>
                    </div>
                    <div>
                        <span style="font-size: 15px; font-weight: bold;">@species</span>
                    </div>
                    <div>
                        <span style="font-size: 10px; color: #696;">Petal length: @petal_length</span><br>
                        <span style="font-size: 10px; color: #696;">Petal width: @petal_width</span>
                    </div>
                </div>
        """)

    def __add_glyphs__(self, with_column_data_source = False):
        if with_column_data_source:
            urlmap = {
                'setosa': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Kosaciec_szczecinkowaty_Iris_setosa.jpg/800px-Kosaciec_szczecinkowaty_Iris_setosa.jpg',
                'versicolor': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Blue_Flag%2C_Ottawa.jpg/800px-Blue_Flag%2C_Ottawa.jpg',
                'virginica': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Iris_virginica.jpg/800px-Iris_virginica.jpg'}
            flowers['imgs'] = [urlmap[x] for x in flowers['species']]
            colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
            flowers['color'] = [colormap[x] for x in flowers['species']]
            flowers['size'] = flowers['sepal_width'] * 4

            setosa = ColumnDataSource(flowers[flowers["species"] == "setosa"])
            versicolor = ColumnDataSource(flowers[flowers["species"] == "versicolor"])
            virginica = ColumnDataSource(flowers[flowers["species"] == "virginica"])

            self.f.circle(x="petal_length", y="petal_width", size='size', fill_alpha=0.2,
                     color="color", line_dash=[5, 3], legend='Setosa', source=setosa)

            self.f.circle(x="petal_length", y="petal_width", size='size', fill_alpha=0.2,
                     color="color", line_dash=[5, 3], legend='Versicolor', source=versicolor)

            self.f.circle(x="petal_length", y="petal_width", size='size', fill_alpha=0.2,
                     color="color", line_dash=[5, 3], legend='Virginica', source=virginica)
        else:
            self.f.circle(x=flowers["petal_length"][flowers["species"] == "setosa"],
                          y=flowers["petal_width"][flowers["species"] == "setosa"],
                          size=flowers['sepal_width'][flowers["species"] == "setosa"] * 4,
                          fill_alpha=0.2, color=flowers['color'][flowers["species"] == "setosa"], line_dash=[5, 3],
                          legend='Setosa')

            self.f.circle(x=flowers["petal_length"][flowers["species"] == "versicolor"],
                          y=flowers["petal_width"][flowers["species"] == "versicolor"],
                          size=flowers['sepal_width'][flowers["species"] == "versicolor"] * 4,
                          fill_alpha=0.2, color=flowers['color'][flowers["species"] == "versicolor"], line_dash=[5, 3],
                          legend='Versicolor')

            self.f.circle(x=flowers["petal_length"][flowers["species"] == "virginica"],
                          y=flowers["petal_width"][flowers["species"] == "virginica"],
                          size=flowers['sepal_width'][flowers["species"] == "virginica"] * 4,
                          fill_alpha=0.2, color=flowers['color'][flowers["species"] == "virginica"], line_dash=[5, 3],
                          legend='Virginica')

    def show_categorical_data(self):
        # prepare the output
        output_file("students.html")
        # create the figure
        self.f = figure(x_range=["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"],
                   y_range=["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"])
        self.f.circle(x=["A", "B"], y=["C", "D"], size=8)
        self.__show__()

    def create_graph_by_df(self):
        df = pd.read_csv('bachelors.csv')  #  Year  Agriculture  Architecture  Art and Performance    Biology   Business
        print(df.head())
        x = df["Year"]
        y = df["Engineering"]
        self.f.line(x, y)
        self.__show__(True)

    def create_simple_graph(self, figure_type: str):
        if figure_type == FT.LINE:
            x = [1, 2, 3, 4, 5]
            y = [6, 7, 8, 9, 10]
        elif figure_type in [FT.TRIANGLE, FT.CIRCLE]:
            x = [3, 7.5, 10]
            y = [3, 6, 9]
        output_file("Graph.html")
        if figure_type == FT.LINE:
            self.f.line(x, y)
        elif figure_type == FT.TRIANGLE:
            self.f.triangle(x, y)
        elif figure_type == FT.CIRCLE:
            self.f.circle(x, y)
        self.__show__()

    def show_candlesticks(self):
        df = pd.DataFrame(MSFT)[:50]
        df["date"] = pd.to_datetime(df["date"])

        inc = df.close > df.open
        dec = df.open > df.close
        w = 12 * 60 * 60 * 1000  # half day in ms

        hover = HoverTool(tooltips = [
            ("Series", "@columns"),
            ("Date", "$x"),
            ("Value", "$y"),
        ])

        # tools = "pan,wheel_zoom,box_zoom,reset,save, hover"
        tools = [HoverTool(), ResetTool(), PanTool(), WheelPanTool(), WheelZoomTool(), SaveTool()]

        p = figure(x_axis_type="datetime", tools=tools, plot_width=1000, title="MSFT Candlestick")
        p.xaxis.major_label_orientation = pi / 4
        p.grid.grid_line_alpha = 0.3

        p.segment(df.date, df.high, df.date, df.low, color="black")
        p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
        p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")

        output_file("candlestick.html", title="candlestick.py example")
        show(p)  # open a browser

    @staticmethod
    def datetime(x):
        return np.array(x, dtype=np.datetime64)

    def show_multiple_stocks(self):
        p1 = figure(x_axis_type="datetime", title="Stock Closing Prices")
        p1.grid.grid_line_alpha = 0.3
        p1.xaxis.axis_label = 'Date'
        p1.yaxis.axis_label = 'Price'

        p1.line(self.datetime(AAPL['date']), AAPL['adj_close'], color='#A6CEE3', legend='AAPL')
        p1.line(self.datetime(GOOG['date']), GOOG['adj_close'], color='#B2DF8A', legend='GOOG')
        p1.line(self.datetime(IBM['date']), IBM['adj_close'], color='#33A02C', legend='IBM')
        p1.line(self.datetime(MSFT['date']), MSFT['adj_close'], color='#FB9A99', legend='MSFT')
        p1.legend.location = "top_left"

        aapl = np.array(AAPL['adj_close'])
        aapl_dates = np.array(AAPL['date'], dtype=np.datetime64)

        window_size = 30
        window = np.ones(window_size) / float(window_size)
        aapl_avg = np.convolve(aapl, window, 'same')

        p2 = figure(x_axis_type="datetime", title="AAPL One-Month Average")
        p2.grid.grid_line_alpha = 0
        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = 'Price'
        p2.ygrid.band_fill_color = "olive"
        p2.ygrid.band_fill_alpha = 0.1

        p2.circle(aapl_dates, aapl, size=4, legend='close',
                  color='darkgrey', alpha=0.2)

        p2.line(aapl_dates, aapl_avg, legend='avg', color='navy')
        p2.legend.location = "top_left"

        output_file("stocks.html", title="stocks.py example")

        show(gridplot([[p1, p2]], plot_width=400, plot_height=400))  # open a browser

    def show_grid_plot(self):
        # Remove rows with NaN values and then map standard states to colors
        elements.dropna(inplace=True)  # if inplace is not set to True the changes are not written to the dataframe
        colormap = {'gas': 'yellow', 'liquid': 'orange', 'solid': 'red'}
        elements['color'] = [colormap[x] for x in elements['standard state']]
        elements['size'] = elements['van der Waals radius'] / 10

        # Create three ColumnDataSources for elements of unique standard states
        gas = ColumnDataSource(elements[elements['standard state'] == 'gas'])
        liquid = ColumnDataSource(elements[elements['standard state'] == 'liquid'])
        solid = ColumnDataSource(elements[elements['standard state'] == 'solid'])

        # Define the output file path
        output_file("elements_gridplot.html")

        # Create the figure object
        f1 = figure()

        # adding glyphs
        f1.circle(x="atomic radius", y="boiling point", size='size',
                  fill_alpha=0.2, color="color", legend='Gas', source=gas)

        f2 = figure()
        f2.circle(x="atomic radius", y="boiling point", size='size',
                  fill_alpha=0.2, color="color", legend='Liquid', source=liquid)

        f3 = figure()
        f3.circle(x="atomic radius", y="boiling point", size='size',
                  fill_alpha=0.2, color="color", legend='Solid', source=solid)

        f = gridplot([[f1, f2], [None, f3]])

        # Save and show the figure
        show(f)

    def ex_7_create_label_annotations_for_span(self):
        # Remove rows with NaN values and then map standard states to colors
        elements.dropna(inplace=True)  # if inplace is not set to True the changes are not written to the dataframe
        colormap = {'gas': 'yellow', 'liquid': 'orange', 'solid': 'red'}
        elements['color'] = [colormap[x] for x in elements['standard state']]
        elements['size'] = elements['van der Waals radius'] / 10

        # Create three ColumnDataSources for elements of unique standard states
        gas = ColumnDataSource(elements[elements['standard state'] == 'gas'])
        liquid = ColumnDataSource(elements[elements['standard state'] == 'liquid'])
        solid = ColumnDataSource(elements[elements['standard state'] == 'solid'])

        # Define the output file path
        output_file("elements_annotations.html")

        # Create the figure object
        f = figure()

        # adding glyphs
        f.circle(x="atomic radius", y="boiling point", size='size',
                 fill_alpha=0.2, color="color", legend='Gas', source=gas)
        f.circle(x="atomic radius", y="boiling point", size='size',
                 fill_alpha=0.2, color="color", legend='Liquid', source=liquid)
        f.circle(x="atomic radius", y="boiling point", size='size',
                 fill_alpha=0.2, color="color", legend='Solid', source=solid)

        # Add axis labels
        f.xaxis.axis_label = "Atomic radius"
        f.yaxis.axis_label = "Boiling point"

        # Calculate the average boiling point for all three groups by dividing the sum by the number of values
        gas_average_boil = sum(gas.data['boiling point']) / len(gas.data['boiling point'])
        liquid_average_boil = sum(liquid.data['boiling point']) / len(liquid.data['boiling point'])
        solid_average_boil = sum(solid.data['boiling point']) / len(solid.data['boiling point'])

        # Create three spans
        span_gas_average_boil = Span(location=gas_average_boil, dimension='width', line_color='yellow', line_width=2)
        span_liquid_average_boil = Span(location=liquid_average_boil, dimension='width', line_color='orange',
                                        line_width=2)
        span_solid_average_boil = Span(location=solid_average_boil, dimension='width', line_color='red', line_width=2)

        # Add spans to the figure
        f.add_layout(span_gas_average_boil)
        f.add_layout(span_liquid_average_boil)
        f.add_layout(span_solid_average_boil)

        # Add labels to spans
        label_span_gas_average_boil = Label(x=80, y=gas_average_boil, text="Gas average boiling point",
                                            render_mode="css",
                                            text_font_size="10px")
        label_span_liquid_average_boil = Label(x=80, y=liquid_average_boil, text="Liquid average boiling point",
                                               render_mode="css",
                                               text_font_size="10px")
        label_span_solid_average_boil = Label(x=80, y=solid_average_boil, text="Solid average boiling point",
                                              render_mode="css",
                                              text_font_size="10px")

        # Add labels to figure
        f.add_layout(label_span_gas_average_boil)
        f.add_layout(label_span_liquid_average_boil)
        f.add_layout(label_span_solid_average_boil)

        # Save and show the figure
        show(f)


my_class = MyBokehClass()
# my_class.create_simple_line_graph()
my_class.ex_7_create_label_annotations_for_span()