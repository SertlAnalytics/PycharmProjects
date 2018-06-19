"""
Description: This module contains different functions for Bokeh server.
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
# importing libraries
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.io import output_file, show, save
from bokeh.models.annotations import LabelSet
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.models.widgets import Select, TextInput, Button, Paragraph
from bokeh.models.widgets import RadioButtonGroup
from bokeh.layouts import layout
from bokeh.models.widgets import Select, Slider
from random import randrange
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from math import radians
from pytz import timezone


class StreamingWidget:
    def __init__(self):
        pass

    def stream_random_points(self):
        #create figure
        f=figure(x_range=(0,11),y_range=(0,11))

        #create columndatasource
        source=ColumnDataSource(data=dict(x=[],y=[]))

        #create glyphs
        # f.circle(x='x',y='y',size=8,fill_color='olive',line_color='yellow',source=source)
        f.line(x='x', y='y', source=source)

        #create periodic function
        def update():
            new_data=dict(x=[randrange(1,10)],y=[randrange(1,10)])
            source.stream(new_data,rollover=15)
            print(source.data)

        #add figure to curdoc and configure callback
        curdoc().add_root(f)
        curdoc().add_periodic_callback(update,1000)

    def stream_financial_data(self):
        #create figure
        f = figure()

        #create columndatasource
        source = ColumnDataSource(dict(x=[1], y=[self.__get_financial_data_from_web__()]))

        #create glyphs
        # f.circle(x='x',y='y',size=8,fill_color='olive',line_color='yellow',source=source)
        f.line(x='x', y='y', source=source)

        #create periodic function
        def update():
            new_data = dict(x=[source.data['x'][-1] + 1], y=[self.__get_financial_data_from_web__()])
            source.stream(new_data, rollover=200)
            print(source.data)

        #add figure to curdoc and configure callback
        curdoc().add_root(f)
        curdoc().add_periodic_callback(update,1000)

    def __get_financial_data_from_web__(self):
        r=requests.get("http://bitcoincharts.com/markets/btcnCNY.html",headers={'User-Agent':'Mozilla/5.0'})
        c=r.content
        soup=BeautifulSoup(c,"html.parser")
        value_raw=soup.find_all("p")
        value_net=float(value_raw[0].span.text)
        return value_net

    def stream_bit_coin_data(self):
        # create figure
        f = figure(x_axis_type='datetime')

        # create webscraping function
        def extract_value():
            r = requests.get("http://bitcoincharts.com/markets/btcnCNY.html", headers={'User-Agent': 'Mozilla/5.0'})
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            value_raw = soup.find_all("p")
            value_net = float(value_raw[0].span.text)
            return value_net

        # create ColumnDataSource
        source = ColumnDataSource(dict(x=[], y=[]))

        # create glyphs
        f.circle(x='x', y='y', color='olive', line_color='brown', source=source)
        f.line(x='x', y='y', source=source)

        # create periodic function
        def update():
            new_data = dict(x=[datetime.now(tz=timezone('Europe/Moscow'))], y=[extract_value()])
            source.stream(new_data, rollover=200)
            print(source.data)

        def update_intermediate(attr, old, new):
            source.data = dict(x=[], y=[])
            update()

        f.xaxis.formatter = DatetimeTickFormatter(
            seconds=["%Y-%m-%d-%H-%m-%S"],
            minsec=["%Y-%m-%d-%H-%m-%S"],
            minutes=["%Y-%m-%d-%H-%m-%S"],
            hourmin=["%Y-%m-%d-%H-%m-%S"],
            hours=["%Y-%m-%d-%H-%m-%S"],
            days=["%Y-%m-%d-%H-%m-%S"],
            months=["%Y-%m-%d-%H-%m-%S"],
            years=["%Y-%m-%d-%H-%m-%S"],
        )

        f.xaxis.major_label_orientation = radians(90)

        # create Select widget
        options = [("okcoinCNY", "Okcoin CNY"), ("btcnCNY", "BTCN China")]
        select = Select(title="Market Name", value="okcoinCNY", options=options)
        select.on_change("value", update_intermediate)

        # add figure to curdoc and configure callback
        lay_out = layout([[f], [select]])
        curdoc().add_root(lay_out)
        curdoc().add_periodic_callback(update, 2000)

    def load_spinning(self):
        # Orbiting planets

        # importing libraries
        from math import cos, sin, radians
        from bokeh.io import curdoc
        from bokeh.models import ColumnDataSource
        from bokeh.plotting import figure

        # Setting up the figure
        p = figure(x_range=(-2, 2), y_range=(-2, 2))

        # Drawing static glyphs
        earth_orbit = p.circle(x=0, y=0, radius=1, line_color='blue', line_alpha=0.5, fill_color=None, line_width=2)
        mars_orbit = p.circle(x=0, y=0, radius=0.7, line_color='red', line_alpha=0.5, fill_color=None, line_width=2)
        sun = p.circle(x=0, y=0, radius=0.2, line_color=None, fill_color="yellow", fill_alpha=0.5)

        # Creating columndatasources for the two moving circles
        earth_source = ColumnDataSource(data=dict(x_earth=[earth_orbit.glyph.radius * cos(radians(0))],
                                                  y_earth=[earth_orbit.glyph.radius * sin(radians(0))]))
        mars_source = ColumnDataSource(data=dict(x_mars=[mars_orbit.glyph.radius * cos(radians(0))],
                                                 y_mars=[mars_orbit.glyph.radius * sin(radians(0))]))

        # Drawing the moving glyphs
        earth = p.circle(x='x_earth', y='y_earth', size=12, fill_color='blue', line_color=None, fill_alpha=0.6,
                         source=earth_source)
        mars = p.circle(x='x_mars', y='y_mars', size=12, fill_color='red', line_color=None, fill_alpha=0.6,
                        source=mars_source)

        # we will generate x and y coordinates every 0.1 seconds out of angles starting from an angle of 0 for both earth and mars
        self.i_earth = 0
        self.i_mars = 0

        # the update function will generate coordinates
        def update():
            self.i_earth += 2  # we will increase the angle of earth by 2 in function call
            self.i_mars += 1
            new_earth_data = dict(x_earth=[earth_orbit.glyph.radius * cos(radians(self.i_earth))],
                                  y_earth=[earth_orbit.glyph.radius * sin(radians(self.i_earth))])
            new_mars_data = dict(x_mars=[mars_orbit.glyph.radius * cos(radians(self.i_mars))],
                                 y_mars=[mars_orbit.glyph.radius * sin(radians(self.i_mars))])
            earth_source.stream(new_earth_data, rollover=1)
            mars_source.stream(new_mars_data, rollover=1)
            print(earth_source.data)  # just printing the data in the terminal
            print(mars_source.data)

        # adding periodic callback and the plot to curdoc
        curdoc().add_periodic_callback(update, 100)
        curdoc().add_root(p)
        # show(p)


streaming = StreamingWidget()
streaming.load_spinning()