from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from app.utils import getdata, getalldata
from app.utils import make_dash_table, create_plot
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

#image_directory = os.getcwd() + '/home/xom/data/'
image_directory = '/home/xom/data/'
image_filename = image_directory+ 'test.png' # replace with your own image
encoded_image_fix = base64.b64encode(open(image_filename, 'rb').read())

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
                    id='my-dropdown',
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
                    id='version-dropdown',
                    options=[
                        {'label': 'version 1.0', 'value': 'v1.0'},
                        {'label': 'version 2.0', 'value': 'v2.0'},
                        {'label': 'version 3.0', 'value': 'v3.0'},
                        {'label': 'version 4.0', 'value': 'v4.0'},
                    ],
                    value='v4.0',
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
        # div hover plot
        html.Div([
            html.P(html.H2('matching graph'),style={'float':'right'}),
            html.Img(id='embedded_plot',
                     src=''.format(encoded_image_fix.decode()),style={'width': '100%', 'display': 'inline-block','height':'auto','vertical-align':'middle'})
        ],style={'width': '30%' ,'display': 'inline-block','vertical-align':'top'}),
        # end div hover plot  
    ])
    # end (graph+ dropdown) + hover plot 

])

process_dict = { 'el_lifetime':'Electron Lifetime [us]','charge_yield': 'Charge Yield [p.e./keV]','light_yield':'Light Yield [p.e./keV]'}
                 
def register_callbacks(dashapp):
    #callback for the main plot
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value'), Input('version-dropdown', 'value')])
    def update_graph(selected_dropdown_value, version_value):
        dftemp = df.loc[(df['version'] == version_value) & (df['process'] == selected_dropdown_value)]
        return create_plot(
            x=dftemp["time"],
            xlabel='time',
            y=dftemp["value"],            
            ylabel=process_dict[selected_dropdown_value],
            error=dftemp['error'],            
            figname=dftemp['figure']
        )
    
    # talke the hover data and the two dropdowns as input to update the graph
    @dashapp.callback(Output("embedded_plot", "src"),[Input("my-graph", "hoverData"),Input('my-dropdown', 'value'), Input('version-dropdown', 'value')])
    def picture_on_hover(hoverData,process,version):
        """
        params hoverData: data on graph hover, and dropdowns
        update the graph as the users passes the mouse on a point or the user changes the drop down values.
        """
        if hoverData is None:
            raise PreventUpdate            
        try:
            dftemp = df.loc[(df['version'] == version) & (df['process'] == process)]
            figtemp = create_plot(
                x=dftemp["time"],
                xlabel='time',
                y=dftemp["value"],
                ylabel=process,
                error=dftemp['error'],
                figname=dftemp['figure']
            )
            # gets the index the point on which the mouse is on
            point_number = hoverData["points"][0]["pointNumber"]
            # gets the corresponding figure name
            figname = str(figtemp["data"][0]["text"].values[point_number]).strip()
            image_path = figname
            encoded_image = base64.b64encode(open(image_path, 'rb').read())
            # the way I found to print out the figure...
            return 'data:image/png;base64,{}'.format(encoded_image.decode())
    
        except Exception as error:
            print(error)
            raise PreventUpdate
