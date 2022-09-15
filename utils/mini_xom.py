from utilix.config import Config
from argparse import ArgumentParser
import json
import cutax
import strax
import straxen
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
st = straxen.contexts.xenonnt()

#need for xom_saver:
import os
from doctest import run_docstring_examples
import sys
from argparse import ArgumentParser
import json
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import subprocess
## figure folder on the machine that host the database and display (grafana)
display_fig_folder = "/home/xom/data/v1.1/test/." 



@straxen.mini_analysis()
def xom_saver(
        var_name, run_id, var_value,
        run_ids = None,
        timestamp = None,
        data=None, 
        figure=None,
        tag = None,
        save_folder = None,
        ):
    """ simple function to save results in xom fomat 
        :param run_ids: optional array for several run ids
        :param var_name: name of the variable of the analysis 
        :param var_value: variable you want to display
        :param timestamp: 
        :param data: additionnal array of data (can be either [val, error, chi2] , can be [x1, x2, x3 ..., x10] bin content etc) 
        :param figure: figure object one want to display in the xom display
        :param tag: analyse specific tag
        :param save_folder: folder to save the json data in 
    """
    serveraddress = {'dali':"90.147.119.208",'lngs':"127.0.0.1"}
    if save_folder == None:
        save_folder = './algorithms/tmp/' 
    
    container = os.getenv('SINGULARITY_NAME')

    result = {}
    if timestamp:
        result['timestamp'] = int(timestamp/1e9)
    else:
        df = st.get_df(str(run_id),
            targets = 'event_info',
            progress_bar=False)
        timestamp = df['time'].iloc[0]
        result['timestamp'] = int(timestamp/1e9)
    result['run_id'] = int(run_id)
    result['var_name'] = var_name
    result['container'] = container
    result['value'] = var_value
    result['tag'] = tag
    result['data'] = data
    
    ## standard json filename to be written in case the database connections fails
    outfname = result['var_name']+'_'+str(result['run_id']) +  '_' + 'cont_' + result['container']
    outjsonname = outfname +'.json'
    ## save the JSON file on disk    
    filename = save_folder + outjsonname
    with open(filename,'w') as f:
        json.dump(result,f)
        f.close()
        
    ## save te figure 
    if figure:
        figname = 'fig_' + result['var_name']+'_'+str(result['run_id']) +  '_' + 'cont_' + result['container'] + '_' + tag +'.png'
        figpath = save_folder + figname
        figure.savefig(figpath)

    ## connect to the database:
    try:
        client = MongoClient(serveraddress['dali'], 27017)
    except:
        print('could not connect to the DB from  {} with address {} '.format(server, serveraddress[server]))

            # Accessing to XOM database
    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    xomdata = database['data']
    print('data = ', data)
    # Uploads data
    xomdata.insert_one(result)
    
    # # copy fig somewhere, for the moment at LNGS
    # process = subprocess.Popen(['scp', figpath, 'xom@xe1t-offlinemon.lngs.infn.it:'+ display_fig_folder], 
    #                        stdout=subprocess.PIPE,
    #                        universal_newlines=True)
 