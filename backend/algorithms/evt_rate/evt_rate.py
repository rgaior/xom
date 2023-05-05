import argparse
import strax
import straxen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
st = straxen.contexts.xenonnt()
sys.path +=['../../../utils/']

import xomlib




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
    rate_1 = df.query("e_ces < 1")
df[df['e_ces'] < 1]['time'].value_counts(bins=nbins,sort=False).values
    rates_10 = df[df['e_ces'] > 10]['time'].value_counts(bins=nbins,sort=False).values
    rates_100 = df[df['e_ces'] > 100]['time'].value_counts(bins=nbins,sort=False).values
    rates_1000 = df[df['e_ces'] > 1000]['time'].value_counts(bins=nbins,sort=False).values
     array_data = {'bins':nbins, 'rates_all':rates_all.tolist(),'rates_10': rates_10.tolist(), 'rates_100':rates_100.tolist(), 'rates_1000':rates_1000.tolist()}
    rate_10 = len(rates_1)/deltat_s
    rate_10 = len(rates_10)/deltat_s
    rate_100 = len(rates_100)/deltat_s
    rate_1000 = len(rates_1000)/deltat_s
    
    
    ### xomdb filling ###
    xomresult = xomlib.Xomresult(analysis_name="evt_rate",
                                 analysis_version = "v0.0",
                                 variable_name='evt_rate',
                                 variable_value=mean,
                                 runid=runid,
                                 data = {"rate_10": rate_10,"rate_100": rate_100,"rate_1000": rate_1000}
    )
    xomresult.save()


    return 0


if __name__ == "__main__":
    main()

