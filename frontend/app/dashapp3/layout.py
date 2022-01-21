from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from app.utils import getdata, getalldata, getvariables
from app.utils import make_dash_table, create_plot, create_plot_with_runid, create_plot_errorx
import app.utils as utils
import os
import base64

df = getalldata()
initvar = 'lightyield'
default_strax = '2.1.1'
default_straxen = '1.2.3'
dftemp = df.loc[ ( df['variable_name']==initvar ) & (df['strax_version']==default_strax) ]
dfvar = getvariables()
dfvartemp = dfvar.loc[ (dfvar['variable_name']==initvar) ]
process_dict = {var:leg for (var, leg) in (zip(dfvar['variable_name'], dfvar['legend_name']) )}
unit_dict = {var:unit for (var, unit) in (zip(dfvar['variable_name'], dfvar['unit']) )}

FIGURE = create_plot(
    x=dftemp["timestamp"].astype('int'),
    xlabel='time',
    y=dftemp["value"],
    ylabel=dfvartemp['legend_name'][0],
    error=dftemp["error"],
    figname=df["figname"]
)

FIGURE_WITH_RUNID = create_plot_with_runid(
    x=dftemp["timestamp"],
    xrunid=dftemp["run_id"],
    xlabel='Time Stamp',
    y=dftemp["value"],
    ylabel=dfvartemp['legend_name'][0],
    yunit=dfvartemp['unit'][0],
    error=dftemp["error"],
    figname=df["figname"]
)


df = getalldata()

def make_version_plot(dftemp):
    figure={
        'data': [
            dict(
                x=dftemp[dftemp['strax_version'] == i]['run_id'],
                y=dftemp[dftemp['strax_version'] == i]['value'],
               error_y=
               dict(
                   type='data', # value of error bar given in data coordinates      
                   array=dftemp[dftemp['strax_version'] == i]['error'],
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
                ) for i in dftemp.strax_version.unique()
            ],
            'layout': dict(
#                xaxis={'title': 'time'},
                yaxis={'title': 'hahah'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
    }
    return figure



# layout = html.Div([
#     html.Div([
#         html.Div([
#             html.A(
#                 html.H2("Back to home page"),
#                 id="home_page",
#                 href="https://xe1t-offlinemon.lngs.infn.it/dash/",
#             ),
#         ],style={'width':'30%','float':'left'}),
#         html.Div([
#             html.A(
#                 html.H2(children="logout",style={'margin-left':'50%'}),
#                 id="logout",
#                 href="https://xe1t-offlinemon.lngs.infn.it/logout/",
#             ),
#         ],style={'width':'30%','float':'right'}),
#     ]),
#     # to be fixed: the space organisation isn't very clean.
#     # I found this quick fix to put the text where I want but it is not very satisfactory
#     html.Br(),
#     html.Br(),
#     html.Br(),
#     html.P(html.H1('Test data')),


image_filename = '/home/xom/xom/frontend/app/assets/logo_xenon.png'
image_svg = '/home/xom/xom/frontend/app/assets/xenonlogo.svg'
logo = '/home/xom/xom/frontend/app/assets/xenonlogo.png'
def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')

encoded_image = base64.b64encode(open(image_svg, 'rb').read()).decode()

def b64_imagesvg(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/svg;base64,' + base64.b64encode(image).decode('utf-8')

variable_option = [{'label':leg, 'value':var} for leg, var in zip(dfvar['legend_name'], dfvar['variable_name'])]
strax_version = utils.getstraxversion()
print('strax_version = ', strax_version)
version_option = [{'label':lab, 'value':val} for lab, val in zip(strax_version, strax_version)]
layout = html.Div(className="body",children=[
    html.Div( className='navbar' ,children=[
        html.Div( className='container' , children=[
            html.Div( className='logodiv',  children=[
                #                html.A("Link to external site",[    html.Img(className='logoim', src=b64_image(logo)), href='https://xe1t-offlinemon.lngs.infn.it/'])
                html.A(html.Img(className='logoim', src=b64_image(logo)), href='https://xe1t-offlinemon.lngs.infn.it/'),
                html.A([html.Span("X"), "enon ",html.Span("O"),"ffline ",html.Span("M"),"onitoring" ], href='https://xe1t-offlinemon.lngs.infn.it/',style={'position':'absolute' ,'margin-left':'1.9em','font-size':22}),
                
                
            ]), #logodiv
        ]) #container
    ]), #navbar
    html.P(html.H2('Version Comparator'),style={'text-align': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='process-dropdown',
            options=variable_option,
            value=dfvar['variable_name'][0],
            clearable=False
        ),
        dcc.Dropdown(
            id='version-dropdown',
            options=version_option,
            multi=True,
            clearable=False,
            value=[default_strax]
         )
    ],style={'width': '38%', 'margin': 'auto'}),
    # end dropdown div process
    html.Div([        
        dcc.Graph(id='my-graph',
                  hoverData={"points": [{"pointNumber":0}]},
                  figure=make_version_plot(dftemp))
    ],style={'width': '70%', 'display': 'center','margin': 'auto'}),
    # end div (graph+ dropdown)

    # # dropdown div for process
    # html.Div([
    #     dcc.Dropdown(
    #         id='process-dropdownx',
    #         options=variable_option,
    #         value=dfvar['variable_name'][0],
    #         clearable=False
    #     ),
    #     dcc.Dropdown(
    #         id='version-dropdown',
    #         options=[
    #             {'label': 'version 1.0', 'value': 'v1.0'},
    #             {'label': 'version 2.0', 'value': 'v2.0'},
    #             {'label': 'version 3.0', 'value': 'v3.0'},
    #             {'label': 'version 4.0', 'value': 'v4.0'},
    #         ],
    #         multi=True,
    #         clearable=False,
    #         value=['v4.0']
    #      )
    # ],
#    ] ,style={'width': '38%', 'margin': 'auto'})
    

    # html.Div([
    
#     html.Div([
#         html.P(html.H2('Electron lifetime')),
#         dcc.Dropdown(
#             id='version-dropdown',
#             options=[
#                 {'label': 'version 1.0', 'value': 'v1.0'},
#                 {'label': 'version 2.0', 'value': 'v2.0'},
#                 {'label': 'version 3.0', 'value': 'v3.0'},
#                 {'label': 'version 4.0', 'value': 'v4.0'},
#             ],
#             multi=True,
#             clearable=False,
#             value=['v4.0']
#         ),
#         html.Div([
#             dcc.Graph(id='graph-lifetime',figure=make_version_plot(df,'el_lifetime'))
#         ]),
#     ], style={'width': '45%','display': 'inline-block','float':'left'}),
#     html.Div([
#         html.P(html.H2('Charge yield')),
#         dcc.Dropdown(
#             id='version-dropdown2',
#             options=[
#                 {'label': 'version 1.0', 'value': 'v1.0'},
#                 {'label': 'version 2.0', 'value': 'v2.0'},
#                 {'label': 'version 3.0', 'value': 'v3.0'},
#                 {'label': 'version 4.0', 'value': 'v4.0'},
#             ],
#             multi=True,
#             clearable=False,
#             value=['v4.0']
#         ),
#         html.Div([
#             dcc.Graph(id='graph-chargeyield',figure=make_version_plot(df,'charge_yield') )
#         ]),
#     ]      , style={'width': '45%','display': 'inline-block','float':'right'}),
    
# ]),
])



def register_callbacks(dashapp):
    #callback for the main plot
#    return 0
    @dashapp.callback(Output('my-graph', 'figure'), [Input('version-dropdown', 'value'), Input('process-dropdown', 'value')])
    def update_graph(version_value, variable_name):
#        version_value = '2.1.2'
        print('version_value = ', version_value)
        dftemp = df.loc[(df['variable_name'] == variable_name)  ]
        dftemp = dftemp[(dftemp['strax_version'].isin(version_value))]
        return make_version_plot(dftemp)
        # return create_plot_with_runid(
        #     x=dftemp["timestamp"],
        #     xrunid=dftemp["run_id"],
        #     xlabel='Time Stamp',
        #     y=dftemp["value"],
        #     ylabel=process_dict[variable_name],
        #     yunit = unit_dict[variable_name],
        #     error=dftemp["error"],
        #     figname=dftemp["figname"]
        # )
#       


