from dash import Dash
import matplotlib
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from textwrap import dedent
from dash.dependencies import Input, Output, State
import base64
import json
from numpy import random
import pandas_datareader.data as web  # requires v0.6.0 or later
import dash_auth
from datetime import datetime
import pandas as pd
import requests


class MyHTML:
    def __init__(self):
        self.html = html

    def Button(self):
        return self.html.Button

    def Div(self):
        return self.html.Div

    def Iframe(self):
        return self.html.Iframe

    def H1(self):
        return self.html.H1

    def H2(self):
        return self.html.H2

    def H3(self):
        return self.html.H3

    def Pre(self):
        return self.html.Pre


class MyDCC:
    def __init__(self):
        self.dcc = dcc

    def Dropdown(self):
        return self.dcc.Dropdown

    def Graph(self):
        return self.dcc.Graph

    def Interval(self):
        return self.dcc.Interval

    def Markdown(self):
        return self.dcc.Markdown

    def RangeSlider(self):
        return self.dcc.RangeSlider
