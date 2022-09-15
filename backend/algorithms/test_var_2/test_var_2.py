import argparse
from resource import RLIMIT_MSGQUEUE
import strax
import straxen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
st = straxen.contexts.xenonnt()
sys.path +=['../utils/']
import xomlib as xl 

def main():
    parser = argparse.ArgumentParser("RunXom")
    parser.add_argument("runs", nargs='+',help="Run number to process")
    parser.add_argument("--container",help=" will fill the xom data base with the container str", default='unfilled')

    args = parser.parse_args()    
    runs = args.runs
    container = args.container
    dflist = []
    run_id = []
    for r in runs:
        run_id.append(str(r).zfill(6) )
        dflist.append(st.get_df(str(r).zfill(6),targets = 'event_info'))
    ######################
    ### loading the df ###
    ######################
    
    df = pd.concat(dflist, ignore_index=True)

    ##########################
    ### doing the analysis ###
    ##########################    
    

    ### preparation of the variables ###

    
    value = np.float64(df['cs1'].mean())
    rms = np.float64(df['cs1'].std())
    value2 = np.float64(df['cs2'].mean())
    rms2 = np.float64(df['cs2'].std())
    
    timestamp = df['time'].iloc[0]
    
    ### xomdb filling ###
    # first we write a json file in a tmp/ directory
    
    result = {}
    result['run_id'] = int(run_id[0])
    
    result['run_ids'] = run_id
    result['variable_name'] = 'test_var_2_a'
    result['container'] = container
    result['timestamp'] = int(timestamp/1e9)
    result['value'] = value
    result['error'] = 0
    result['chisquared'] = None
    result['tag'] = 'test'
    result['data'] = None
    outfname = result['variable_name']+'_'+str(result['run_id']) +  '_' + 'cont_' + result['container']
    
    outjsonname = outfname +'.json'

    result2 = {}
    result2['run_id'] = int(run_id[0])
    
    result2['run_ids'] = run_id
    result2['variable_name'] = 'test_var_2_b'
    result2['container'] = container
    result2['timestamp'] = int(timestamp/1e9)
    result2['value'] = value2
    result2['error'] = rms2
    result2['chisquared'] = None
    result2['tag'] = 'test'
    result2['data'] = None
    outfname2 = result2['variable_name']+'_'+str(result2['run_id']) +  '_' + 'cont_' + result2['container']
    
    
    outjsonname2 = outfname2 +'.json'

    # write the json file:
    xl.SaveData(result,'./algorithms/test_var_2/tmp/' + outjsonname)
    xl.SaveData(result2,'./algorithms/test_var_2/tmp/' + outjsonname2)
    
    # write on the XOM data base at LNGS
    xl.UploadDataDict(result, 'dali')
    xl.UploadDataDict(result2, 'dali')


    return 0


if __name__ == "__main__":
    main()

