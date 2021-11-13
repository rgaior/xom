from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from app.utils import getdata, getalldata
from app.utils import make_dash_table, create_plot, create_plot_errorx
import os
import base64
df = getalldata()

dftemp = df.sort_values(by=['time'])
dftemp = dftemp[ (dftemp['process']=='el_lifetime') & (dftemp['version']=='v4.0')]
print ('times = ', df['time'],flush=True)
print ('times sorted ? = ', dftemp['time'],flush=True)
sel = ''
FIGURE = create_plot(
    x=dftemp["time"],
    xlabel='time',
    y=dftemp["value"],
    ylabel='temp',
    error=dftemp["error"],
    figname=dftemp["figure"]
)

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
    # main div with the (graph + dropdowns) +  fig 
    html.Div([
        # div (graph + dropdowns)
        html.Div([
            # dropdown div for process
            html.Div([
                dcc.Dropdown(
                    id='process-dropdownx',
                    options=[
                        {'label': 'Electron Lifetime', 'value': 'el_lifetime'},
                        {'label': 'Charge Yield', 'value': 'charge_yield'},
                        {'label': 'Light Yield', 'value': 'light_yield'}
                    ],
                    value='el_lifetime',
                    clearable=False
                ),
            ],style={'width': '48%', 'display': 'inline-block'}),
            # end dropdown div process
            # dropdown div version
            html.Div([
                dcc.Dropdown(
                    id='process-dropdowny',
                    options=[
                        {'label': 'Electron Lifetime', 'value': 'el_lifetime'},
                        {'label': 'Charge Yield', 'value': 'charge_yield'},
                        {'label': 'Light Yield', 'value': 'light_yield'}
                    ],
                    value='charge_yield',
                    clearable=False
                ),
            ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        # end dropdown div version
            html.Div([        
                dcc.Graph(id='my-graph',
                          hoverData={"points": [{"pointNumber":0}]},
                          figure=FIGURE)
            ],style={'width': '90%', 'display': 'inline-block'}),
        ],style={'width': '60%', 'display': 'inline-block'}),
        # end div (graph+ dropdown)
    ])
    # end (graph+ dropdown) + hover plot 

])

process_dict = { 'el_lifetime':'Electron Lifetime [us]','charge_yield': 'Charge Yield [p.e./keV]','light_yield':'Light Yield [p.e./keV]'}
                 
def register_callbacks(dashapp):
    #callback for the main plot
    @dashapp.callback(Output('my-graph', 'figure'), [Input('process-dropdownx', 'value'), Input('process-dropdowny', 'value')])
    def update_graph(processx, processy):
        version = 'v4.0'
        dftempx = df.loc[(df['version'] ==  version) & (df['process'] ==  processx) ]
        dftempy = df.loc[(df['version'] ==  version) & (df['process'] ==  processy) ]
        return create_plot_errorx(
            x=dftempx["value"],
            xlabel=process_dict[processx],
            y=dftempy["value"],            
            ylabel=process_dict[processy],
            error=dftempy['error'],            
            errorx=dftempx['error'],            
            figname=dftempy['figure']
        )
    
