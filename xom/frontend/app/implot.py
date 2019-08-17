
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models.widgets import PreText, Select, DateRangeSlider
import datetime
from bokeh.io import curdoc
from bokeh.layouts import row, column, layout, gridplot
import pandas as pd
#output_file("toolbar.html")
from pymongo import MongoClient
client = MongoClient()
#login_manager = LoginManager()
db = client.test1
collection = db.inventory


#SOURCE_TICKERS = ['kr', 'ng', 'rn']
SOURCE_TICKERS = ['Krypton', 'Neutron Gun', 'Radon']
#PROCESS_TICKERS = ['el_lifetime', 'charge_yield', 'light_yield']
PROCESS_TICKERS = ['Electron Lifetime', 'Charge Yield', 'Light Yield']
source_dict = {'Krypton':'kr','Neutron Gun':'ng','Radon':'rn'}
process_dict = {'Electron Lifetime':'el_lifetime','Charge Yield':'charge_yield','Light Yield':'light_yield'}

def nix(val, lst):
    return [x for x in lst if x != val]



# setup widget:
ticker1 = Select(value='Krypton', options=SOURCE_TICKERS)
ticker2 = Select(value='Charge Yield', options=PROCESS_TICKERS)
startslider = datetime.datetime(2017, 1, 1)
endslider = datetime.datetime(2018, 1, 1)
date_range_slider = DateRangeSlider(title="Date Range: ", start=startslider, end=endslider, value=(startslider, endslider), step=1)

TOOLTIPS = """
    <div>
        <div>
            <img
                src="@figure" height="300" alt="@figure" width="300"
                style="float: left; margin: 0px 15px 15px 0px;"
                border="2"
            ></img>
        </div>
    </div>
"""


def get_data():
    t1 = source_dict[ticker1.value]
    t2 = process_dict[ticker2.value]
    dates = date_range_slider.value_as_datetime
    date0 = datetime.datetime.timestamp(dates[0])
    date1 = datetime.datetime.timestamp(dates[1])
    data_type = 'calibration'
    #selects only calibration data
    # selects calibration file & the source of calibration & the dates
    mydata = collection.find({"info.source" : t1.lower(), "info.type":data_type, "info.start_time": {"$gte" : date0*1e9, "$lte" : date1*1e9},})
    data = []
    if data_type!=None:
        for d in mydata:
            data.append(d['processes'][t2])
        df = pd.DataFrame.from_dict(data, orient='columns')    
    #adds the path in /static/ for the figure 
    df['figure'] = '/static/images/' + df['figure']
    return df

# attempt to find the minimum/maximum value of time in the dB
#mintime = collection.find().sort({"info.run":-1}).limit(1) 
df0 = get_data()
# setup plot
source = ColumnDataSource(df0)
source_static = ColumnDataSource(df0)
### allow for the choice of the tool in the bokeh toolbox
tools = 'pan,wheel_zoom,xbox_select,reset'
### defines the figure
plot_width = 550
calib = figure(plot_width=plot_width, plot_height=350, tooltips=TOOLTIPS,
              tools=tools,x_axis_label='RUN', y_axis_label='value')
calib.circle('run_number', 'value', size=20, source=source,
             selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)


# set up callbacks 
def ticker1_change(attrname, old,new):
    update()
def ticker2_change(attrname, old,new):
    update()
def date_range_slider_change(attrname, old,new):
    update()

def update(selected=None):
    data = get_data()
    source.data = source.from_df(data)
    source_static.data = source.data
    

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)
date_range_slider.on_change('value', date_range_slider_change)

#def selection_change(attrname, old, new):
#    data = get_data()
#    t1, t2 = ticker1.value, ticker2.value
#    data = get_data(t1, t2)
#     selected = source.selected.indices
#     if selected:
#         data = data.iloc[selected, :]
#         print ("the data here:", data)
#    update_stats(data, t1, t2)

#source.selected.on_change('indices', selection_change)


# set up layout                                                                                                                     
widgets = column(ticker1, ticker2)
widgetfake = column(date_range_slider,width=1)
widget2 = column(date_range_slider,width=plot_width)
main_row = row(widgets,calib)
#series = column(ts1, ts2)
#layout = column(main_row,widget2)
layout = gridplot([[widgets,calib], [None, widget2]])

# initialize                                                                                                                        
update()

def plot(doc):
    doc.add_root(layout)
    doc.title = "Calibration vs Run number"



