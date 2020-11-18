from datetime import datetime as dt
import plotly.graph_objects as go

import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output

from app.utils import getdata

def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value'), Input('version-dropdown', 'value')])
    def update_graph(selected_dropdown_value, version_value):
#        df = pdr.get_data_yahoo(selected_dropdown_value, start=dt(2017, 1, 1), end=dt.now())
        df = getdata(selected_dropdown_value,version_value)
        print('roro value',df.value)
        print('roro time',df.time)

        return {
            'data': [{
                'x': df.time,
                'y': df.value,
                'error_y':dict(
                    type='data', # value of error bar given in data coordinates
                    array=df.error,
                    visible=True)
            }],
            'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
        }
