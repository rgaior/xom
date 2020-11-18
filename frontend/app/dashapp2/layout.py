import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash_table.Format import Format, Scheme, Sign, Symbol

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# make a sample data frame with 6 columns
np.random.seed(0)

from datetime import datetime as dt
from app.utils import getdata, getalldata
from app.utils import make_dash_table, create_plot

#df = getalldata()
df = getdata("el_lifetime","v3.0")

layout = html.Div([
    html.Div([
        html.Div([
            html.A(
                html.H2("Back to home page"),
                id="home_page",
                href="https://xe1t-offlinemon.lngs.infn.it/dash/",
            ),
        ],style={'width':'30%','float':'left'}),
        html.Div([
            html.A(
                html.H2(children="logout",style={'margin-left':'50%'}),
                id="logout",
                href="https://xe1t-offlinemon.lngs.infn.it/logout/",
            ),
        ],style={'width':'30%','float':'right'}),
    ]),
    # to be fixed: the space organisation isn't very clean.
    # I found this quick fix to put the text where I want but it is not very satisfactory
    html.Br(),
    html.Br(),
    html.Br(),
    html.P(html.H1('Test data of electron lifetime')),


    # main div with the (graph + dropdowns) +  fig 
    html.Div([
        html.Div(
            dcc.Graph(id='g1', config={'displayModeBar': False}),
            className='four columns'
        ),
        html.Div(
            dcc.Graph(id='g2', config={'displayModeBar': False}),
            className='four columns'
        ),
        html.Div(
            dcc.Graph(id='g3', config={'displayModeBar': False}),
            className='four columns'
        )
    ], className='row'),
    html.Br(),
    html.Br(),
    html.Br(),
    html.P(html.H1('selected points table')),
    html.Div([
        dash_table.DataTable(
            id='table',
#            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            columns=[{
            'id': 'run_number',
            'name': 'Run Number',
            'type': 'numeric'
            }, {
            'id': 'value',
            'name': u'Value',
            'type': 'numeric',
            'format': Format(precision=4),
            },
            {'id': 'error',
            'name': u'Error',
            'type': 'numeric',
            'format': Format(precision=4)
             },
            {'id': 'time',
            'name': u'Time',
            'type': 'string',
#            'format': Format(precision=4)
            }
                
#            columns=[{"name": i, "id": i} for i in df[['run_number','value','error']].columns],
        ]
    )
    ],style={'width':'50%','float':'middle'}),

])

    
def get_figure(dfsel, x_col, y_col, selectedpoints, selectedpoints_local):

    if selectedpoints_local and selectedpoints_local['range']:
        ranges = selectedpoints_local['range']
        selection_bounds = {'x0': ranges['x'][0], 'x1': ranges['x'][1],
                            'y0': ranges['y'][0], 'y1': ranges['y'][1]}
    else:
        selection_bounds = {'x0': np.min(dfsel[x_col]), 'x1': np.max(dfsel[x_col]),
                            'y0': np.min(dfsel[y_col]), 'y1': np.max(dfsel[y_col])}

    # set which points are selected with the `selectedpoints` property
    # and style those points with the `selected` and `unselected`
    # attribute. see
    # https://medium.com/@plotlygraphs/notes-from-the-latest-plotly-js-release-b035a5b43e21
    # for an explanation
    return {
        'data': [{
            'x': dfsel[x_col],
            'y': dfsel[y_col],
            'text': dfsel.index,
            'textposition': 'top',
            'selectedpoints': selectedpoints,
            'customdata': dfsel.index,
            'type': 'scatter',
            'mode': 'markers+text',
            'marker': { 'color': 'rgba(0, 116, 217, 0.7)', 'size': 12 },
            'unselected': {
                'marker': { 'opacity': 0.3 },
                # make text transparent when not selected
                'textfont': { 'color': 'rgba(0, 0, 0, 0)' }
            }
        }],
        'layout': {
            'margin': {'l': 50, 'r': 0, 'b': 50, 't': 0},
            'dragmode': 'select',
            'hovermode': False,
            'xaxis':{"title":x_col,"color": "#000000"},
            'yaxis':{"title":y_col,"color": "#000000"},

            # Display a rectangle to highlight the previously selected region
            'shapes': [dict({
                'type': 'rect',
                'line': { 'width': 1, 'dash': 'dot', 'color': 'darkgrey' }
            }, **selection_bounds
            )]
        }
    }

# this callback defines 3 figures
# as a function of the intersection of their 3 selections
def register_callbacks(dashapp):
    @dashapp.callback(
        [Output('g1', 'figure'),
         Output('g2', 'figure'),
         Output('g3', 'figure'),
         Output('table','data' )],
        [Input('g1', 'selectedData'),
         Input('g2', 'selectedData'),
         Input('g3', 'selectedData'),
        ]
    )
    def callback(selection1, selection2, selection3):
        selectedpoints = df.index
        for selected_data in [selection1, selection2, selection3]:
            if selected_data and selected_data['points']:
                selectedpoints = np.intersect1d(selectedpoints,
                    [p['customdata'] for p in selected_data['points']])
                #        dftable = df.iloc[[selectedpoints]]
                #        print ('dftable = ', dftable,flush=True)
                #        dftemp = df
                #        get_data(dftemp,selectedpoints,flush=True)
#        print (df.loc[df.index],flush=True)
        print (df.loc[selectedpoints],flush=True)
        return [get_figure(df, "time", "value", selectedpoints, selection1),
                get_figure(df, "time", "error", selectedpoints, selection2),
                get_figure(df, "time", "chi2", selectedpoints, selection3),
                df.loc[selectedpoints].to_dict('records')]


# @app.callback(
#         Output("output-1","children"),
#         [Input("save-button","n_clicks")],
#         [State("table","data")]
#         )

# def selected_data_to_csv(nclicks,table1): 
#     if nclicks == 0:
#         raise PreventUpdate
#     else:
#         pd.DataFrame(table1).to_csv('H://R//filename.csv',index=False)
#         return "Data Submitted"
