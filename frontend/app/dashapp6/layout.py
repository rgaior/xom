from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from app.utils import getdata, getalldata, getvariables
from app.utils import make_dash_table, create_plot, create_plot_with_runid, create_plot_errorx
import os
import base64
df = getalldata()
initvar = 'lightyield'
default_strax = '2.1.1'
default_straxen = '1.2.3'
dftemp = df.loc[ ( df['variable_name']==initvar ) & (df['strax_version']==default_strax)  & ( df['straxen_version']==default_straxen) ]
dfvar = getvariables()
dfvartemp = dfvar.loc[ (dfvar['variable_name']==initvar) ]
print('tes ======== ', dfvartemp)
process_dict = {var:leg for (var, leg) in (zip(dfvar['variable_name'], dfvar['legend_name']) )}
unit_dict = {var:unit for (var, unit) in (zip(dfvar['variable_name'], dfvar['unit']) )}
print('process_dict = ' , process_dict)

image_folder = '/xom/images/'

FIGURE = create_plot(
    x=dftemp["timestamp"].astype('int'),
    xlabel='time',
    y=dftemp["value"],
    ylabel=dfvartemp['legend_name'][0],
    error=dftemp["error"],
    figname=dftemp["figname"]
)

FIGURE_WITH_RUNID = create_plot(
#FIGURE_WITH_RUNID = create_plot_with_runid(
#    x=dftemp["timestamp"],
#    xrunid=dftemp["run_id"],
    x=dftemp["run_id"],
    xlabel='Time Stamp',
    y=dftemp["value"],
    ylabel=dfvartemp['legend_name'][0],
#    yunit=dfvartemp['unit'][0],
    error=dftemp["error"],
    figname=df["figname"]
)


image_filename = '/home/xom/xom/frontend/app/assets/logo_xenon.png'
image_svg = '/home/xom/xom/frontend/app/assets/xenonlogo.svg'
logo = '/home/xom/xom/frontend/app/assets/xenonlogo.png'

def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')

def decode_image(image_path):
    return base64.b64encode(open(image_path, 'rb').read()).decode()


encoded_image = base64.b64encode(open(image_svg, 'rb').read()).decode()

def b64_imagesvg(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/svg;base64,' + base64.b64encode(image).decode('utf-8')


variable_option = [{'label':leg, 'value':var} for leg, var in zip(dfvar['legend_name'], dfvar['variable_name'])]
layout = html.Div(className="body",children=[
    html.Div( className='navbar' ,children=[
        html.Div( className='container' , children=[
            html.Div( className='logodiv',  children=[
#                html.A("Link to external site",[    html.Img(className='logoim', src=b64_image(logo)), href='https://xe1t-offlinemon.lngs.infn.it/'])
                html.A(html.Img(className='logoim', src=b64_image(logo)), href='https://xe1t-offlinemon.lngs.infn.it/'),
                html.A([html.Span("X"), "enon ",html.Span("O"),"ffline ",html.Span("M"),"onitoring" ], href='https://xe1t-offlinemon.lngs.infn.it/',style={'position':'absolute' ,'margin-left':'1.9em','font-size':22}),


            ]), #logodiv
            html.Nav( className='navlink',  children=[
                html.Ul([
                    html.Li(html.A(html.Img(className='logoim', src=b64_image(logo), style={'align':'middle'}),  href='https://xe1t-offlinemon.lngs.infn.it/') ),
                    html.Li(html.A(html.Img(className='logoim', src=b64_image(logo), style={'align':'middle'}),  href='https://xe1t-offlinemon.lngs.infn.it/logout')),
                    html.Li(html.A(html.Img(className='logoim', src=b64_image(logo), style={'align':'middle'}),  href='https://xe1t-offlinemon.lngs.infn.it/dash/app5/')),]
                ), # UL ends
            ]), #navlink Nav
            
        ]) #container
    ]), #navbar
    html.P(html.H2('Quick View'),style={'text-align': 'center'}),
    # dropdown div for process
    html.Div([
        dcc.Dropdown(
            id='process-dropdownx',
            options=variable_option,
            value=dfvar['variable_name'][0],
            clearable=False
        ),
    ],style={'width': '38%', 'margin': 'auto'}),
    # end dropdown div process
    html.Div([        
        dcc.Graph(id='my-graph',
                  hoverData={"points": [{"pointNumber":0}]},
                  figure=FIGURE_WITH_RUNID)
    ],style={'width': '70%', 'display': 'center','margin': 'auto'}),
    # end div (graph+ dropdown)
    # div hover plot
    html.Div([
        html.P(html.H2('matching graph'),style={'float':'right'}),
        html.Img(id='embedded_plot',
                 src=''.format(decode_image(logo)),style={'width': '100%', 'display': 'inline-block','height':'auto','vertical-align':'middle'})
    ],style={'width': '30%' ,'display': 'inline-block','vertical-align':'top'}),
    # end div hover plot  
    
]) #body

#    'el_lifetime':'Electron Lifetime [us]','charge_yield': 'Charge Yield [p.e./keV]','light_yield':'Light Yield [p.e./keV]'}
                 
def register_callbacks(dashapp):
    #callback for the main plot
    @dashapp.callback(Output('my-graph', 'figure'), [Input('process-dropdownx', 'value')])
    def update_graph(variable_name):
        dftemp = df.loc[(df['variable_name'] == variable_name)  & (df['strax_version']==default_strax)  & ( df['straxen_version']==default_straxen) ]
        dfvartemp = dfvar.loc[ (dfvar['variable_name']==  variable_name) ]
        print('dfvartemp = ', dfvartemp)
#        return create_plot_with_runid(
        return create_plot(
#            x=dftemp["timestamp"],
            x=dftemp["run_id"],
#            xrunid=dftemp["run_id"],
            xlabel='Time Stamp',
            y=dftemp["value"],
            ylabel=process_dict[variable_name],
#            yunit = unit_dict[variable_name],
            error=dftemp["error"],
            figname=dftemp["figname"]
        )
     
    @dashapp.callback(Output("embedded_plot", "src"),[Input("my-graph", "hoverData"), Input('process-dropdownx', 'value')])
    def picture_on_hover(hoverData,variable_name):
        """
        params hoverData: data on graph hover, and dropdowns
        update the graph as the users passes the mouse on a point or the user changes the drop down values.
        """
        print('tata')
        
        if hoverData is None:
            raise PreventUpdate            
        try:
            dftemp = df.loc[(df['variable_name'] == variable_name)  & (df['strax_version']==default_strax)  & ( df['straxen_version']==default_straxen) ]
            dfvartemp = dfvar.loc[ (dfvar['variable_name']==  variable_name) ]
            print('dfvartemp = ', dfvartemp)
#            figtemp = create_plot_with_runid(
            figtemp = create_plot(
#                x=dftemp["timestamp"],
#                xrunid=dftemp["run_id"],
                x=dftemp["run_id"],
                xlabel='Time Stamp',
                y=dftemp["value"],
                ylabel=process_dict[variable_name],
#                yunit = unit_dict[variable_name],
                error=dftemp["error"],
                figname=dftemp["figname"]
            )

            # gets the index the point on which the mouse is on
            point_number = hoverData["points"][0]["pointNumber"]
            # gets the corresponding figure name
            print('figtemp["data"] = ', figtemp["data"])
            figname = str(figtemp["data"][0]["text"].values[point_number]).strip()
            image_path =  image_folder +figname
            print('image+path = ', image_path)
            encoded_image = b64_image(image_path)
            # the way I found to print out the figure...
#            return 'data:image/png;base64,{}'.format(encoded_image.decode())
            return encoded_image
    
        except Exception as error:
            print(error)
            raise PreventUpdate
