"""
Description: This module is the central module for plotting - which can be reused within dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-08-22
"""
import plotly.plotly as py
import plotly.tools as pt
import plotly.graph_objs as go

import numpy as np

women_bins = np.array([-600, -623, -653, -650, -670, -578, -541, -411, -322, -230])
men_bins = np.array([600, 623, 653, 650, 670, 578, 541, 360, 312, 170])
women_with_dogs_bins = np.array([-0, -3, -308, -281, -245, -231, -212, -132, -74, -76])
men_with_dogs_bins = np.array([0, 1, 300, 273, 256, 211, 201, 170, 145, 43])

y = list(range(0, 100, 10))

layout = go.Layout(yaxis=go.layout.YAxis(title='Age'),
                   xaxis=go.layout.XAxis(
                       range=[-1200, 1200],
                       tickvals=[-1000, -700, -300, 0, 300, 700, 1000],
                       ticktext=[1000, 700, 300, 0, 300, 700, 1000],
                       title='Number'),
                   barmode='overlay',
                   bargap=0.1)

data = [go.Bar(y=y,
               x=men_bins,
               orientation='h',
               name='Men',
               hoverinfo='x',
               marker=dict(color='powderblue')
               ),
        go.Bar(y=y,
               x=women_bins,
               orientation='h',
               name='Women',
               text=-1 * women_bins.astype('int'),
               hoverinfo='text',
               marker=dict(color='seagreen')
               ),
        go.Bar(y=y,
               x=men_with_dogs_bins,
               orientation='h',
               hoverinfo='x',
               showlegend=False,
               opacity=0.5,
               marker=dict(color='teal')
               ),
        go.Bar(y=y,
               x=women_with_dogs_bins,
               orientation='h',
               text=-1 * women_bins.astype('int'),
               hoverinfo='text',
               showlegend=False,
               opacity=0.5,
               marker=dict(color='darkgreen')
               )]

pt.set_credentials_file(username='JWSertl', api_key='MY50ds5YelfzmDnSwWd5')
# py.sign_in('JWSertl', api_key='GSH5WQQ536UPER3AQG4W')
# pt.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')
py.iplot(dict(data=data, layout=layout), filename='stacked_bar_pyramid', sharing='public')