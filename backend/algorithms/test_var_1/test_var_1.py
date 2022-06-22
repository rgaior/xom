import argparse
import strax
import straxen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
st = straxen.contexts.xenonnt()
sys.path +=['../utils/']
import xomlib as xl 
import constant as cst 

def main():
    parser = argparse.ArgumentParser("RunXom")
    parser.add_argument("runs", nargs='+',help="Run number to process")
    parser.add_argument("--container",help=" will fill the xom data base with the container str", default='unfilled')

    args = parser.parse_args()    
    runs = args.runs
    container = args.container

    run_id = str(runs[0]).zfill(6)
    ######################
    ### loading the df ###
    ######################
    df = st.get_df(str(run_id),
            targets = 'event_info',
            progress_bar=True)
    # except: 
    #     print("couldn't load event_info")

    ##########################
    ### doing the analysis ###
    ##########################    
    #rate = 0.1 #Hz
    dt = 60 #s
    t_init = df['time'].iloc[0]
    t_final = df['endtime'].iloc[-1]
    deltat_ns = t_final -t_init
    deltat_s = deltat_ns/1e9
    dt_ns = dt*1e9
    nbins  = int(deltat_ns/dt_ns) 
    rate_total = len(df)/deltat_s
    print('tot rate = ', rate_total)

    ### preparation of the variables ###
    value = rate_total
    timestamp = df['time'].iloc[0]
    rates_all = df['time'].value_counts(bins=nbins,sort=False).values
    rates_10 = df[df['e_ces'] > 10]['time'].value_counts(bins=nbins,sort=False).values
    rates_100 = df[df['e_ces'] > 100]['time'].value_counts(bins=nbins,sort=False).values
    rates_1000 = df[df['e_ces'] > 1000]['time'].value_counts(bins=nbins,sort=False).values
    data = {'bins':nbins, 'rates_all':rates_all.tolist(),'rates_10': rates_10.tolist(), 'rates_100':rates_100.tolist(), 'rates_1000':rates_1000.tolist()}

    ### xomdb filling ###
    # first we write a json file in a tmp/ directory
    
    result = {}
    result['run_id'] = int(run_id)
    
    result['run_ids'] = [int(run_id)]
    result['variable_name'] = 'test_var_1'
    result['container'] = container
    result['timestamp'] = int(timestamp/1e9)
    result['value'] = value
    result['error'] = np.sqrt(value)
    result['chisquared'] = None
    result['tag'] = 'test'
    result['data'] = data
    outfname = result['variable_name']+'_'+str(result['run_id']) +  '_' + 'cont_' + result['container']
    outjsonname = outfname+'.json'

    fig = plt.figure(figsize=(9,9), dpi=1200)
    plt.plot(data['rates_all'])
    outfigname = outfname + ".png"
    result['figname'] = outfigname
    # save the figure
    figpath = './algorithms/test_var_1/tmp/' + outfigname
    fig.savefig(figpath)
    
    # write the json file:
    xl.SaveData(result,'./algorithms/test_var_1/tmp/' + outjsonname)
    
    # write on the XOM data base at LNGS
    xl.UploadDataDict(result, 'dali')

    xl.UploadFile(figpath, 'xom@xe1t-offlinemon.lngs.infn.it:'+ cst.figfolder)

    return 0


if __name__ == "__main__":
    main()

