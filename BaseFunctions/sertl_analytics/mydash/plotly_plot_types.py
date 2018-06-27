"""
Description: This module is the main module for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-17
"""


import pandas as pd
import sertl_analytics.environment  # init some environment variables during load - for security reasons
from dash import Dash
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from datetime import datetime
import quandl
import os
import numpy as np
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly import tools


class MyPlotly:
    def __init__(self):
        self.f = None

    def read_csv(self):
        self.df = pd.read_csv('salaries.csv')
        print(self.df.head())
        self.df.plot()
        # self.df.boxplot()
        # Dash.config
        plt.show()

    def heatmap(self):
        #######
        # Side-by-side heatmaps for Sitka, Alaska,
        # Santa Barbara, California and Yuma, Arizona
        # using a shared temperature scale.
        ######

        df1 = pd.read_csv('data/2010SitkaAK.csv')
        df2 = pd.read_csv('data/2010SantaBarbaraCA.csv')
        df3 = pd.read_csv('data/2010YumaAZ.csv')

        trace1 = go.Heatmap(
            x=df1['DAY'],
            y=df1['LST_TIME'],
            z=df1['T_HR_AVG'],
            colorscale='Jet',
            zmin=5, zmax=40  # add max/min color values to make each plot consistent
        )
        trace2 = go.Heatmap(
            x=df2['DAY'],
            y=df2['LST_TIME'],
            z=df2['T_HR_AVG'],
            colorscale='Jet',
            zmin=5, zmax=40
        )
        trace3 = go.Heatmap(
            x=df3['DAY'],
            y=df3['LST_TIME'],
            z=df3['T_HR_AVG'],
            colorscale='Jet',
            zmin=5, zmax=40
        )

        fig = tools.make_subplots(rows=1, cols=3,
                                  subplot_titles=('Sitka, AK', 'Santa Barbara, CA', 'Yuma, AZ'),
                                  shared_yaxes=True,  # this makes the hours appear only on the left
                                  )
        fig.append_trace(trace1, 1, 1)
        fig.append_trace(trace2, 1, 2)
        fig.append_trace(trace3, 1, 3)

        fig['layout'].update(  # access the layout directly!
            title='Hourly Temperatures, June 1-7, 2010'
        )
        pyo.plot(fig, filename='html_files/AllThree.html')

    def heatmap_exercise(self):
        df = pd.read_csv('data/flights.csv')

        # Define a data variable
        data = [go.Heatmap(
            x=df['year'],
            y=df['month'],
            z=df['passengers']
        )]

        # Define the layout
        layout = go.Layout(
            title='Flights'
        )
        # Create a fig from data and layout, and plot the fig
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/solution8.html')

        #######
        # Excellent! This shows two distinct trends - an increase in
        # passengers flying over the years, and a greater number of
        # passengers flying in the summer months.
        ######

    def distribution_plot(self):
        snodgrass = [.209, .205, .196, .210, .202, .207, .224, .223, .220, .201]
        twain = [.225, .262, .217, .240, .230, .229, .235, .217]

        hist_data = [snodgrass, twain]
        group_labels = ['Snodgrass', 'Twain']

        fig = ff.create_distplot(hist_data, group_labels, bin_size=[.005, .005])
        pyo.plot(fig, filename='html_files/SnodgrassTwainDistplot.html')

    def histograms(self):
        df = pd.read_csv('data/FremontBridgeBicycles.csv')

        # Convert the "Date" text column to a Datetime series:
        df['Date'] = pd.to_datetime(df['Date'])

        # Add a column to hold the hour:
        df['Hour'] = df['Date'].dt.time

        # Let pandas perform the aggregation
        df2 = df.groupby('Hour').sum()

        trace1 = go.Bar(
            x=df2.index,
            y=df2['Fremont Bridge West Sidewalk'],
            name="Southbound",
            width=1  # eliminates space between adjacent bars
        )
        trace2 = go.Bar(
            x=df2.index,
            y=df2['Fremont Bridge East Sidewalk'],
            name="Northbound",
            width=1
        )
        data = [trace1, trace2]

        layout = go.Layout(
            title='Fremont Bridge Bicycle Traffic by Hour',
            barmode='stack'
        )
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/fremont_bridge.html')

    def histogram_mpg(self):
        df = pd.read_csv('../data/mpg.csv')

        data = [go.Histogram(
            x=df['mpg']
        )]

        layout = go.Layout(
            title="Miles per Gallon Frequencies of<br>\
            1970's Era Vehicles"
        )
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/basic_histogram.html')

    def histogram_gender(self):
        #######
        # This histogram compares heights by gender
        ######
        df = pd.read_csv('data/arrhythmia.csv')

        data = [go.Histogram(
            x=df[df['Sex'] == 0]['Height'],
            opacity=0.75,
            name='Male'
        ),
            go.Histogram(
                x=df[df['Sex'] == 1]['Height'],
                opacity=0.75,
                name='Female'
            )]

        layout = go.Layout(
            barmode='overlay',
            title="Height comparison by gender"
        )
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/basic_histogram2.html')

    def box_plot(self):
        snodgrass = [.209, .205, .196, .210, .202, .207, .224, .223, .220, .201]
        twain = [.225, .262, .217, .240, .230, .229, .235, .217]

        data = [
            go.Box(
                y=snodgrass,
                name='QCS',
                boxpoints='all',
                jitter=0.3,
                pointpos=0
            ),
            go.Box(
                y=twain,
                name='MT',
                boxpoints='outliers'
            )
        ]
        layout = go.Layout(
            title='Comparison of three-letter-word frequencies<br>\
            between Quintus Curtius Snodgrass and Mark Twain'
        )
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/box3.html')

    def box_plot_exercise(self):
        df = pd.read_csv('data/abalone.csv')

        # take two random samples of different sizes:
        a = np.random.choice(df['rings'], 30, replace=False)
        b = np.random.choice(df['rings'], 100, replace=False)

        # create a data variable with two Box plots:
        data = [
            go.Box(
                y=a,
                name='A'
            ),
            go.Box(
                y=b,
                name='B'
            )
        ]

        # add a layout
        layout = go.Layout(
            title='Comparison of two samples taken from the same population'
        )

        # create a fig from data & layout, and plot the fig
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/solution5.html')

    def bubble_chart(self):
        file = 'data/mpg.csv'
        df = pd.read_csv(file)
        print(df.head())
        print(df.info())
        print(df.columns)
        trace_0 = go.Scatter(x=df['horsepower'],
                             y=df['mpg'],
                             text=df['name'],
                             mode='markers',
                             marker=dict(
                                 size=2*df['cylinders'],
                                 color=df['cylinders'],
                                 showscale=True
                             )
                        )

        data = [trace_0]
        # layout
        layout = go.Layout(title='Bubble Chart')
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/bubble.html')

    def bubble_chart_exercise(self):
        file = 'data/mpg.csv'
        df = pd.read_csv(file)
        # create data by choosing fields for x, y and marker size attributes
        data = [go.Scatter(
            x=df['displacement'],
            y=df['acceleration'],
            text=df['name'],
            mode='markers',
            marker=dict(size=df['weight'] / 500)
        )]

        # create a layout with a title and axis labels
        layout = go.Layout(
            title='Vehicle acceleration vs. displacement',
            xaxis=dict(title='displacement'),
            yaxis=dict(title='acceleration = seconds to reach 60mph'),
            hovermode='closest'
        )

        # create a fig from data & layout, and plot the fig
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/solution4.html')


    def bar_chart_with_csv_data(self):
        file = 'data/2018WinterOlympics.csv'
        df = pd.read_csv(file)
        # df_2 = df[df['DIVISION'] == '1']
        # df_2.set_index('NAME', inplace=True)
        # df_3 = df_2[[col for col in df_2.columns if col.startswith('POP')]]
        print(df.head())
        print(df.info())

        trace_0 = go.Bar(x=df['NOC'], y=df['Gold'], name='Gold', marker={'color':'#FFD700'})
        trace_1 = go.Bar(x=df['NOC'], y=df['Silver'], name='Silver', marker={'color':'#9EA0A1'})
        trace_2 = go.Bar(x=df['NOC'], y=df['Bronze'], name='Bronze', marker={'color':'#CD7F32'})

        data = [trace_0, trace_1, trace_2]
        layout = go.Layout(title='Medals')
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig)

    def bar_chart_exercise(self):
        # create a DataFrame from the .csv file:
        df = pd.read_csv('data/mocksurvey.csv', index_col=0)

        # create traces using a list comprehension:
        data = [go.Bar(
            y=df.index,  # reverse your x- and y-axis assignments
            x=df[response],
            orientation='h',  # this line makes it horizontal!
            name=response
        ) for response in df.columns]

        # create a layout, remember to set the barmode here
        layout = go.Layout(
            title='Mock Survey Results',
            barmode='stack'
        )

        # create a fig from data & layout, and plot the fig.
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html_files/solution3b.html')

    def lines_with_csv_data(self):
        file = 'data/nst-est2017-alldata.csv'
        df = pd.read_csv(file)
        df_2 = df[df['DIVISION'] == '1']
        df_2.set_index('NAME', inplace=True)
        df_3 = df_2[[col for col in df_2.columns if col.startswith('POP')]]
        print(df_3.head())
        print(df_3.info())

        data = [go.Scatter(x=[col[-4:] for col in df_3.columns], y=df_3.loc[name], mode='lines', name=name) for name in df_3.index]
        pyo.plot(data)

    def line_chart_exercise(self):
        ####################
        ## NOTE: ADVANCED SOLUTION THAT USES ONLY PURE DF CALLS
        ## THIS IS FOR MORE ADVANCED PANDAS USERS TO TAKE A LOOK AT! :)

        #######
        # Objective: Using the file 2010YumaAZ.csv, develop a Line Chart
        # that plots seven days worth of temperature data on one graph.
        # You can use a for loop to assign each day to its own trace.
        ######

        # Create a pandas DataFrame from 2010YumaAZ.csv
        df = pd.read_csv('data/2010YumaAZ.csv')

        # Define a data variable
        data = [{
            'x': df['LST_TIME'],
            'y': df[df['DAY'] == day]['T_HR_AVG'],
            'name': day
        } for day in df['DAY'].unique()]

        # Define the layout
        layout = go.Layout(
            title='Daily temperatures from June 1-7, 2010 in Yuma, Arizona',
            hovermode='closest'
        )

        # Create a fig from data and layout, and plot the fig
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html/solution2b.html')

    def lines(self):
        np.random.seed(56)
        x_values = np.linspace(0, 1, 100)
        y_values = np.random.randn(100)
        trace_0 = go.Scatter(x=x_values,
                           y=y_values + 5,
                           mode='markers', name='markers'
                        )

        trace_1 = go.Scatter(x=x_values,
                           y=y_values,
                           mode='lines', name='markers'
                        )

        trace_2 = go.Scatter(x=x_values,
                             y=y_values - 5,
                             mode='lines+markers', name='lines_markers'
                             )

        data = [trace_0, trace_1, trace_2]
        # layout
        layout = go.Layout(title='Line Object')
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html/lines.html')

    def scatter(self):
        np.random.seed(42)
        random_x = np.random.randint(1, 101, 100)
        random_y = np.random.randint(1, 101, 100)
        data = [go.Scatter(x=random_x,
                           y=random_y,
                           mode='markers',
                           marker=dict(
                                size=12,
                                color='rgb(51,204, 153)',
                                symbol='pentagon',
                                line={'width':2}
                                )
                           )]
        # layout
        layout = go.Layout(title='Title', xaxis={'title': 'My X AXIS'}, yaxis={'title': 'My X AXIS'},
                           hovermode='closest')
        fig = go.Figure(data=data, layout=layout)
        pyo.plot(fig, filename='html/scatter.html')


    def print(self):
        if self.f is None:
            print('a')

    def read_stock_data_from_morningstar(self):
        start = datetime(2015, 2, 9)
        end = datetime(2018, 5, 24)
        f = web.DataReader('BB', 'morningstar', start, end)
        print(f)
        # print(f.head())

    def read_stock_data_from_quandl(self):
        symbol = 'WIKI/AAPL'  # or 'AAPL.US'
        symbol = 'FRED/GDP'
        start = datetime(2015, 2, 9)
        end = datetime(2018, 5, 24)
        # df = web.DataReader(symbol, 'quandl', '2017-01-01', '2018-06-22')
        quandl.ApiConfig.api_key = os.environ["quandl_apikey"]
        mydata = quandl.get(symbol, start_date="2001-12-31", end_date="2018-12-31")
        mydata = quandl.get_table('MER/F1', compnumber="39102", paginate=True)
        # mydata = quandl.get_table('ZACKS/FC', ticker='AAPL')
        mydata = quandl.get_table('WIKI/PRICES', qopts={'columns': ['ticker', 'date', 'close', 'open', 'high', 'low']},
                                ticker=['AAPL', 'MSFT','FSE/EON_X'],
                                date={'gte': '2016-01-01', 'lte': '2019-12-31'})
        # mydata = quandl.get('FSE/EON_X', start_date='2016-01-01', end_date='2019-12-31', collapse='daily',
        #                     transformation='rdiff', rows=2000)
        mydata = quandl.get('FSE/EON_X', start_date='2016-01-01', end_date='2019-12-31', collapse='daily')

        print(mydata.info())
        print(mydata)


my_plotly = MyPlotly()
my_plotly.heatmap_exercise()