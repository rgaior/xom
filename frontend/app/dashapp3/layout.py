from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from app.utils import getdata, getalldata
from app.utils import make_dash_table, create_plot
import os

df = getalldata()

# Figure={
#     'data': [
#             dict(
#                 x=df[df['version'] == i]['time'],
#                 y=df[df['version'] == i]['value'],
#                 errory = df[df['version'] == i]['error'],
#                 mode='markers',
#                     opacity=0.7,
#                     marker={
#                         'size': 15,
#                         'line': {'width': 0.5, 'color': 'white'}
#                     },
#                     name=i
#                 ) for i in df.version.unique()
#             ],
#             'layout': dict(
# #                xaxis={'title': 'time'},
#                 yaxis={'title': 'Electron lifetime'},
#                 margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#                 legend={'x': 0, 'y': 1},
#                 hovermode='closest'
#             )
#     }


# FIGURE = create_plot(
#     x=df["time"],
#     xlabel='time',
#     y=df["value"],
#     ylabel='temp',
#     error=df["error"],
#     figname=df["figure"]
# )

process_dict = { 'el_lifetime':'Electron Lifetime [us]','charge_yield': 'Charge Yield [p.e./keV]','light_yield':'Light Yield [p.e./keV]'}
def make_version_plot(dftemp,process):
    dftemp = dftemp[dftemp['process']==process]
    figure={
        'data': [
            dict(
                x=dftemp[dftemp['version'] == i]['time'],
                y=dftemp[dftemp['version'] == i]['value'],
               error_y=
               dict(
                   type='data', # value of error bar given in data coordinates      
                   array=dftemp[dftemp['version'] == i]['error'],
                   visible=True),
#                error_y = dftemp[dftemp['version'] == i]['error'],
                visible=True,
                mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 5,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in dftemp.version.unique()
            ],
            'layout': dict(
#                xaxis={'title': 'time'},
                yaxis={'title': process_dict[process]},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
    }
    return figure



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
    html.P(html.H1('Test data')),

    html.Div([

        html.Div([
            html.P(html.H2('Electron lifetime')),
            dcc.Dropdown(
                id='version-dropdown',
                options=[
                    {'label': 'version 1.0', 'value': 'v1.0'},
                    {'label': 'version 2.0', 'value': 'v2.0'},
                    {'label': 'version 3.0', 'value': 'v3.0'},
                    {'label': 'version 4.0', 'value': 'v4.0'},
                ],
                multi=True,
                clearable=False,
                value=['v4.0']
            ),
        html.Div([
            dcc.Graph(id='graph-lifetime',figure=make_version_plot(df,'el_lifetime'))
        ]),
    ], style={'width': '45%','display': 'inline-block','float':'left'}),
    html.Div([
        html.P(html.H2('Charge yield')),
            dcc.Dropdown(
                id='version-dropdown2',
                options=[
                    {'label': 'version 1.0', 'value': 'v1.0'},
                    {'label': 'version 2.0', 'value': 'v2.0'},
                    {'label': 'version 3.0', 'value': 'v3.0'},
                    {'label': 'version 4.0', 'value': 'v4.0'},
                ],
                multi=True,
                clearable=False,
                value=['v4.0']
            ),
        html.Div([
            dcc.Graph(id='graph-chargeyield',figure=make_version_plot(df,'charge_yield') )
        ]),
    ]      , style={'width': '45%','display': 'inline-block','float':'right'}),
    
    ]),
    ])



def register_callbacks(dashapp):
    #callback for the main plot
    @dashapp.callback(Output('graph-lifetime', 'figure'), [Input('version-dropdown', 'value')])
    def update_graph(version_value):
        process = 'el_lifetime'
        print ('versions = ', df.version.unique(),flush=True)
        print ('version_value = ', df['version'],flush=True)
        dftemp = df[(df['version'].isin(version_value))]
        return make_version_plot(dftemp,process)


    @dashapp.callback(Output('graph-chargeyield', 'figure'), [Input('version-dropdown2', 'value')])
    def update_graph_charge(version_value):
        process = 'charge_yield'
        print ('versions = ', df.version.unique(),flush=True)
        print ('version_value = ', df['version'],flush=True)
        dftemp = df[(df['version'].isin(version_value))]
        return make_version_plot(dftemp,process)

    # talke the hover data and the two dropdowns as input to update the graph


