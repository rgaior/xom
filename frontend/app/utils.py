import pandas as pd
from app.extensions import mongo
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def getdata_from_variable(variablename):
    mydata = mongo.db['data'].find({"variable_name" :variablename})
    df = pd.DataFrame(list(mydata))
    return df

def getvariables():
    myvar = mongo.db['variables'].find()
    df = pd.DataFrame(list(myvar))
    print('varibale = ', df)
    return df

def getdata(current_variable, current_version):
    mydata = mongo.db[current_version].find({"info.source" : "kr","info.type":"calibration"})
    data = []
    for d in mydata:
        data.append(d['processes'][current_variable])
    df = pd.DataFrame.from_dict(data, orient='columns')
    return df

def getalldata():
    mydata = mongo.db['data'].find()
    df = pd.DataFrame(list(mydata))
    straxversion = mydata.distinct('strax_version')
    return  df

def getstraxversion():
    mydata = mongo.db['data'].find()
    straxversion = mydata.distinct('strax_version')
    return straxversion

    
import dash_html_components as html


def make_dash_table(selection, df):
    """ Return a dash defintion of an HTML table from a Pandas dataframe. """

    df_subset = df.loc[df["NAME"].isin(selection)]
    table = []

    for index, row in df_subset.iterrows():
        rows = []
        rows.append(html.Td([row["NAME"]]))
        rows.append(html.Td([html.Img(src=row["IMG_URL"])]))
        rows.append(html.Td([row["FORM"]]))
        rows.append(
            html.Td([html.A(href=row["PAGE"], children="Datasheet", target="_blank")])
        )
        table.append(html.Tr(rows))

    return table



def _create_axis(axis_type, variation="Linear", title=None):
    """
    Creates a 2d or 3d axis.
    :params axis_type: 2d or 3d axis
    :params variation: axis type (log, line, linear, etc)
    :parmas title: axis title
    :returns: plotly axis dictionnary
    """

    if axis_type not in ["3d", "2d"]:
        return None

    default_style = {
        "background": "rgb(255, 255, 255)",
        "gridcolor": "rgb(230, 230, 230)",
        "zerolinecolor": "rgb(0, 0,0)",
    }

    if axis_type == "3d":
        return {
            "showbackground": True,
            "backgroundcolor": default_style["background"],
            "gridcolor": default_style["gridcolor"],
            "title": title,
            "type": variation,
            "zerolinecolor": default_style["zerolinecolor"],
        }

    if axis_type == "2d":
        return {
            "backgroundcolor": "rgb(255,255,255)",
            "gridcolor": default_style["gridcolor"],
            "title": title,
            "zerolinecolor": default_style["zerolinecolor"],
            "color": "#000000",
        } 


def _black_out_axis(axis):
    axis["showgrid"] = True
    axis["zeroline"] = True
    axis["color"] = "rgb(0,0,0)"
    return axis


def _create_layout(layout_type, xlabel, ylabel):
    """ Return dash plot layout. """

    base_layout = {
        "font": {"family": "Raleway", "size":18, "color":"#7f7f7f"},
        "hovermode": "closest",
        "margin": {"r": 50, "t": 20, "l": 100, "b": 100},
        "showlegend": False,
    }

    if layout_type == "scatter3d":
        base_layout["scene"] = {
            "xaxis": _create_axis(axis_type="3d", title=xlabel),
            "yaxis": _create_axis(axis_type="3d", title=ylabel),
            "zaxis": _create_axis(axis_type="3d", title=xlabel, variation="log"),
            "camera": {
                "up": {"x": 0, "y": 0, "z": 1},
                "center": {"x": 0, "y": 0, "z": 0},
                "eye": {"x": 0.08, "y": 2.2, "z": 0.08},
            },
        }

    elif layout_type == "histogram2d":
        base_layout["xaxis"] = _black_out_axis(
            _create_axis(axis_type="2d", title=xlabel)
        )
        base_layout["yaxis"] = _black_out_axis(
            _create_axis(axis_type="2d", title=ylabel)
        )
        base_layout["plot_bgcolor"] = "black"
        base_layout["paper_bgcolor"] = "black"
        base_layout["font"]["color"] = "white"

    elif layout_type == "scatter":
        base_layout["xaxis"] = _black_out_axis(
            _create_axis(axis_type="2d", title=xlabel)
        )
        base_layout["yaxis"] = _black_out_axis(
            _create_axis(axis_type="2d", title=ylabel)
        )
#        base_layout["xaxis"] = _create_axis(axis_type="2d", title=xlabel)
#        base_layout["yaxis"] = _create_axis(axis_type="2d", title=ylabel)
#        base_layout["plot_bgcolor"] = "white"
#        base_layout["plot_bgcolor"] = "rgb(255, 255, 255)"
#        base_layout["paper_bgcolor"] ="white"
        #"rgb(230, 230, 230)"

    return base_layout


def create_plot(
    x,
    xlabel,
    y,
    ylabel,
    error,
    figname
):
    data = [
        {
            "mode":"markers",
            "coloraxis":"black",
            "x": x,
            "y": y,
            "error_y": 
            dict(
                type='data', # value of error bar given in data coordinates
                array=error,
                visible=True),
            "text": figname
        }
    ]
    layout = _create_layout("scatter", xlabel, ylabel)
    return {"data": data,   'layout':layout}

def create_legend(title, unit):
    return(title + ' [' + unit + ']')

def create_plot_with_runid(
        x,
        xrunid,
        xlabel,
        y,
        ylabel,
        yunit,
        error,
        figname
):

    fig = make_subplots(rows=1, cols=1)
    #                        vertical_spacing=0.02    
    x = pd.to_datetime(x, unit='s')
    fig.add_trace(go.Scatter(mode='markers',x=x, y=y, error_y=dict(array=error),xaxis="x1"))
    fig.add_trace(go.Scatter(mode='markers',x=xrunid, y=y, error_y=dict(array=error),xaxis="x2",line=None))
    fig.update_layout(height=500, width=1000,
                      yaxis=dict(title= create_legend(ylabel, yunit)),
                      xaxis1=dict(position=1, range=[np.min(x), np.max(x)], title=dict(text=xlabel) ) ,
                      xaxis2=dict(position =1, range=[np.min(xrunid), np.max(xrunid)], overlaying='x',showgrid=False,title='Run ID'),
                      font={"family": "Raleway", "size":18, "color":"black"},showlegend= False)
    fig["data"][0]["text"] = figname
    #    layout = _create_layout("scatter", xlabel, ylabel)
    return fig
#{"data": data,   'layout':layout}

def create_plot_errorx(
    x,
    xlabel,
    y,
    ylabel,
    error,
    errorx,
    figname
):
    data = [
        {
            "mode":"markers",
            "coloraxis":"black",
            "x": x,
            "y": y,
            "error_y": 
            dict(
                type='data', # value of error bar given in data coordinates
                array=error,
                visible=True),
            "error_x": 
            dict(
                type='data', # value of error bar given in data coordinates
                array=errorx,
                visible=True),
            "text": figname
        }
    ]
    layout = _create_layout("scatter", xlabel, ylabel)
    return {"data": data,   'layout':layout}
