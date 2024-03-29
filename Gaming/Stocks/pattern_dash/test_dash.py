import dash_core_components as dcc
import dash_html_components as html
import dash
import datetime
from dash.dependencies import Input, Output, State, Event

app = dash.Dash()

app.layout = html.Div([
    dcc.Interval(id='my-interval'),
    dcc.RadioItems(id='set-time',
        value=1000,
        options=[
            {'label': 'Every second', 'value': 1000},
            {'label': 'Every 5 seconds', 'value': 5000},
            {'label': 'Off', 'value': 60*60*1000} # or just every hour
        ]),
    html.Div(id='display-time')
])


@app.callback(
    Output('display-time', 'children'),
    events=[Event('my-interval', 'interval')])
def display_time():
    return str(datetime.datetime.now())


@app.callback(
    Output('my-interval', 'interval'),
    [Input('set-time', 'value')])
def update_interval(value):
    print('update_interval: {}'.format(value))
    return value

if __name__ == '__main__':
    app.run_server(debug=True)


    # @self.app.callback(
    #     Output('my-interval', 'interval'),
    #     [Input('my_interval_option', 'value')])
    # def update_interval_period(value):
    #     print('__init_interval_setting_callback__: {}'.format(value))
    #     return 10 * 1000 if value == 'run' else 100 * 1000