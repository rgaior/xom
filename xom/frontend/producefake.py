import os
import pymongo
import datetime
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
import matplotlib.pyplot as plt

client = pymongo.MongoClient()
client.drop_database('test1')
db = client.test1  #change to client.(NameOfDatabase)
collection = db.inventory #change to db.(NameOfCollection)

appfolder = '/Users/gaior/XENON/code/site/gitxom/xom/xom/frontend/app/'
folder = appfolder + '/static/images/'
def func(x, mean, std, k):
    return k*norm.pdf(x,mean,std)
def produceimage(run,proc,value,error):
    datapoint = 1000
    y = np.random.normal(value,error,1000)
    bins = np.arange(np.min(y),np.max(y),1)
    hist, binedge = np.histogram(y, bins=bins)
    fig, ax = plt.subplots()
    plt.hist(y, bins=bins,histtype='step')
    plt.plot(bins[:-1], func(bins[:-1],100,10,1000))
    popt, pcov = curve_fit(func, bins[:-1], hist,p0=[value,error,datapoint])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    textstr = 'RUN: ' + str(run) + ' process: ' + proc 
    # place a text box in upper left in axes coords
#    fig = plt.figure()
    ax.text(0.05, 0.25, textstr, transform=ax.transAxes, fontsize=30,
        verticalalignment='top', bbox=props)
    fig.savefig(folder + '/'+str(run) + '_'+ proc+'.png')
    plt.close()
#produceimage(10,"el_li",100,10)

#plt.show()


def checkifexist(tocheck, array, down,up,step):    
    print (tocheck)
    if (tocheck not in array) & (tocheck < up) & (tocheck > down):
        ok = True
    else:
        ok = False
        if (tocheck >= up):
            tocheck -= step
        elif (tocheck <= down):
            tocheck += step
        else:
            factor = np.sign((np.random.uniform(-1,1)))*1
            tocheck += factor*step        
    if (ok!=True):
        checkifexist(tocheck, array,up,down,step)
    return tocheck

sources = ['kr','rn','ng']
processes = ['el_lifetime','light_yield','charge_yield']
namedict = {'el_lifetime':'electron lifetime [us]','light_yield':'light_yield','charge_yield':'charge_yield'}

def produceoneentry(runs):
    run_down, run_up, run_step = 8000, 10000, 1
    run = np.random.randint(8000,10000)
    checkifexist(run, runs,run_down, run_up, run_step)

    straxen_version = '"v_1.0"'
    start_time = np.random.randint(1491229119999552900,1497229119999552900)
    end_time = start_time + np.random.randint(10e9,1e12)
    # to do if needed
    filename = '170403_1418'

    source = np.random.choice(sources)
    user = 'mlotfi'
    original_entries = np.random.randint(1000,100000)
    prod_time = 1561628288663011072
    type = 'calibration'

    dict_info = {'run':run, 'straxen_version': straxen_version, 'start_time':start_time, 'filename': filename, 'source': source, 'user':user, 'original entries': original_entries, 'offline production time': prod_time, 'type': type,'end_time':end_time}
    
    
    
    process_dict = {}
    for proc in processes:
        process = proc
        run_number = run
        name = namedict[process]
        figname = str(run)+'_'+process +'.png'
        chi2 = np.random.uniform(10,1000)
        error = np.random.uniform(0.5,10)
        ndof = 26
        value = np.random.uniform(500,600)
        time = datetime.datetime.fromtimestamp(int(start_time/1e9)).strftime("%m/%d/%Y %H:%M:%S")
        pvalue = np.random.uniform(0,1)
        pdict= {'run_number':run_number, 'name': name, 'figure': figname, 'chi2':chi2, 'error': error, 'ndof': ndof, 'value':value, 'time': time, 'pvalue': pvalue}
        process_dict[proc] = pdict
        produceimage(run,proc,value,error)
    entry = {'info':dict_info,'processes':process_dict}
#    print (entry['info']['run'])
    return entry



numberofentries = 100
runs = []
data = []
for i in range(numberofentries):
    entry = produceoneentry(runs)
    runs.append(entry['info']['run'])
    data.append(entry)

test = collection.insert_many(data)








# # entriesJson = [{u'info': {u'run': 8424, u'straxen version': u'"v_1.0"', u'start_time': 1491229119999552900, u'filename': u'170403_1418', u'source': u'kr', u'user': u'mlotfi', u'original entries': 280427, u'offline production time': 1561628288663011072, u'type': u'calibration', u'end_time': 1491232722691476310}, u'processes': {u'el_lifetime': {u'run_number': 8424, u'name': u'electron lifetime [us]', u'figure': u'8424_el_lifetime.png', u'chi2': 59.876193256122924, u'error': 1.1137058602087875, u'ndof': 26, u'value': 578.8748388036427, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}, u'charge_yield': {u'run_number': 8424, u'name': u'charge_yield', u'figure': u'8424_41.0keV_charge_yield.png', u'chi2': 426.44474527519355, u'error': 0.07654734143930865, u'ndof': 78, u'value': 72.4980349286444, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}, u'light_yield': {u'run_number': 8424, u'name': u'light_yield', u'figure': u'8424_32.0kev_light_yield.png', u'chi2': 724.12849269972, u'error': 0.00555469172582402, u'ndof': 49, u'value': 11.752065370493746, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}}},
# # {u'info': {u'run': 8425, u'straxen version': u'"v_1.0"', u'start_time': 1491329119999552900, u'filename': u'170404_1805', u'source': u'kr', u'user': u'mlotfi', u'original entries': 280427, u'offline production time': 1561728288663011072, u'type': u'calibration', u'end_time': 1491332722691476310}, u'processes': {u'el_lifetime': {u'run_number': 8425, u'name': u'electron lifetime [us]', u'figure': u'8425_el_lifetime.png', u'chi2': 59.876193256122924, u'error': 1.1137058602087875, u'ndof': 26, u'value': 578.8748388036427, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}, u'charge_yield': {u'run_number': 8425, u'name': u'charge_yield', u'figure': u'8425_41.0keV_charge_yield.png', u'chi2': 426.44474527519355, u'error': 0.07654734143930865, u'ndof': 78, u'value': 72.4980349286444, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}, u'light_yield': {u'run_number': 8425, u'name': u'light_yield', u'figure': u'8425_32.0kev_light_yield.png', u'chi2': 724.12849269972, u'error': 0.00555469172582402, u'ndof': 49, u'value': 11.752065370493746, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}}},
# # {u'info': {u'run': 8426, u'straxen version': u'"v_1.0"', u'start_time': 1491429119999552900, u'filename': u'170405_2151', u'source': u'rn', u'user': u'mlotfi', u'original entries': 280427, u'offline production time': 1561828288663011072, u'type': u'calibration', u'end_time': 1491432722691476310}, u'processes': {u'el_lifetime': {u'run_number': 8426, u'name': u'electron lifetime [us]', u'figure': u'8426_el_lifetime.png', u'chi2': 59.876193256122924, u'error': 1.1137058602087875, u'ndof': 26, u'value': 578.8748388036427, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}, u'charge_yield': {u'run_number': 8426, u'name': u'charge_yield', u'figure': u'8426_41.0keV_charge_yield.png', u'chi2': 426.44474527519355, u'error': 0.07654734143930865, u'ndof': 78, u'value': 72.4980349286444, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}, u'light_yield': {u'run_number': 8426, u'name': u'light_yield', u'figure': u'8426_32.0kev_light_yield.png', u'chi2': 724.12849269972, u'error': 0.00555469172582402, u'ndof': 49, u'value': 11.752065370493746, u'time': u'2017-04-03 09:18:39', u'pvalue': u'0.0'}}}]

