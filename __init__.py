"""
Main source code of XoM Frontend
"""
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Label
from flask import Flask, request, render_template, abort, Response, make_response
import pymongo
from pymongo import MongoClient
from flask_pymongo import PyMongo
import pandas as pd
import numpy as np
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://a1c7091f1f8b41b8b9efe13fbc52c7e9@sentry.io/1873687",
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)
#app.config.from_pyfile('/home/xom/flask/xom/xom/frontend/app/config.py')


"""
Connecting to the XoM MongoDB
"""
#app.config['MONGO_DBNAME'] = 'xom' # name of database on mongo
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/xom"
mongo = PyMongo(app)
variable_names = ['el_lifetime', 'light_yield', 'charge_yield']
version_names = ["v1.0", "v2.0", "v3.0", "v4.0"]

# Create a plot
def create_figure(current_variable, current_version):

    """
    Accessing data
    """
    dataframe = pd.DataFrame(list(mongo.db[current_version].find()))
    xdata = []
    ydata = []
    sxdata = []
    sydata = []
    for i in range(len(dataframe)):
        xdata.append(dataframe.processes[i][current_variable]['time'])
        ydata.append(dataframe.processes[i][current_variable]['value'])
        sxdata.append(0)
        sydata.append(dataframe.processes[i][current_variable]['error'])

    p = figure(x_range=xdata, plot_height=100)
    mytext = Label(x=0, y=0, text=str(len(dataframe)))
    p.add_layout(mytext)
    p.sizing_mode = 'scale_width'

    """
    Plotting data points with error bars
    """
    p.circle(xdata, ydata, color='red')
    sx = []
    sy = []
    for x, y, yerr in zip(xdata, ydata, sydata):
        sx.append((x, x))
        sy.append((y - yerr, y + yerr))
    p.multi_line(sx, sy, color='red')
    p.xaxis.axis_label = 'Time [CET]'
    p.yaxis.axis_label = dataframe.processes[0][current_variable]['name']

    return p

"""
Main web page showing plots
"""
@app.route('/', methods= ['POST', 'GET'])
def MainXom():

    # Determine the selected feature
    if request.method == 'POST':
        res = make_response("")
        res.set_cookie("variable", request.form.get('variable'), 60*60*24*15)
        res.set_cookie("version", request.form.get('version'), 60*60*24*15)
        res.set_cookie("variable2", request.form.get('variable2'), 60*60*24*15)
        res.set_cookie("version2", request.form.get('version2'), 60*60*24*15)
        res.set_cookie("variable3", request.form.get('variable3'), 60*60*24*15)
        res.set_cookie("version3", request.form.get('version3'), 60*60*24*15)
        return res, 302
    
    cookies = request.cookies
    current_variable = cookies.get("variable")
    current_version = cookies.get("version")
    current_variable2 = cookies.get("variable2")
    current_version2 = cookies.get("version2")
    current_variable3 = cookies.get("variable3")
    current_version3 = cookies.get("version3")
    
    #current_variable = request.args.get("variable")
    if current_variable == None:
        current_variable = 'el_lifetime'
    #current_version = request.args.get("version")
    if current_version == None:
        current_version = "v4.0"

    current_variable2 = request.args.get("variable2")
    if current_variable2 == None:
        current_variable2 = 'light_yield'
    current_version2 = request.args.get("version2")
    if current_version2 == None:
        current_version2 = "v4.0"

    current_variable3 = request.args.get("variable3")
    if current_variable3 == None:
        current_variable3 = 'charge_yield'
    current_version3 = request.args.get("version3")
    if current_version3 == None:
        current_version3 = "v4.0"
    """
    cookies = request.cookies
    current_variable = cookies.get("variable")
    current_version = cookies.get("version")
    current_variable2 = cookies.get("variable2")
    current_version2 = cookies.get("version2")
    current_variable3 = cookies.get("variable3")
    current_version3 = cookies.get("version3")
    """
    # Create plots
    #plot = create_figure(current_variable, current_version)
    plot2 = create_figure(current_variable2, current_version2)
    plot3 = create_figure(current_variable3, current_version3)




    """
    Passing plot to the template
    """
    #script, div = components(plot)
    script2, div2 = components(plot2)
    script3, div3 = components(plot3)
    #kwargs = {'plot_script': plot_script, 'plot_div': plot_div}
    #kwargs['variable'] = variable
    #kwargs['version'] = version
    if request.method == 'GET':
        #return render_template('xom.html', **kwargs)
        return render_template("xom.html", script2=script2, div2=div2, script3=script3, div3=div3,
            variable_names=variable_names, version_names=version_names,  current_variable=current_variable,
            current_version=current_version, current_variable2=current_variable2,
            current_version2=current_version2, current_variable3=current_variable3,
            current_version3=current_version3)
    abort(404)
    abort(Response('XoM'))


@app.route('/_get_plot', methods=['GET','POST'])
def get_plot():

    # extract variable, version via ajax post - contained in request.form
    current_variable = request.args.get("variable")
    current_version = request.args.get("version")

    # the updated/new plot
    plot = create_figure(current_variable, current_version)


    script, div = components(plot)

    return render_template('update_content.html', div=div, script=script)

if __name__ == '__main__':
    app.run(debug=True)
