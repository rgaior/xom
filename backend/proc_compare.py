#!/usr/bin/env python

import os
from argparse import ArgumentParser
from socket import timeout
import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from utilix.config import Config
from bson.json_util import dumps
import json
from datetime import timezone, datetime, timedelta
import strax
import straxen
import sys
import pprint 
import numpy as np
import time
import configparser
import shlex
import subprocess
sys.path +=['../utils/']
import constant
import locklib as ll
import dblib as dbl
import importlib
analysismodule = importlib.import_module("analysis")  
import logging



            
        
def main():
    print()
    print("--------------------------------------")
    print("XOM BACKEND PROCESS COMPARE module    ")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("proc_compare")

    parser.add_argument("--verbose", help="Shows informations and statistics about the database", action='store_true')

    args = parser.parse_args()
    verbose = args.verbose
    logging.basicConfig(filename='../logs/backend.log', level=logging.INFO)
    logging.info('Started')

    command_file = 'list_of_commands.txt'

    rundb = pymongo_collection('runs')
    db_client = dbl.connect_to_DB('dali')
    xomdb = db_client['xom']

    # Accessing to Data collection
    xomvariablesdb = xomdb['variables']
    xomdatadb = xomdb['data']

    #############################
    ### sets up the xomconfig ###
    #############################
    xomconfig = configparser.ConfigParser()
    xomconfig.sections()
    xomconfig.read('../utils/xomconfig.cfg')
    analysis_names = xomconfig.sections()


    a = 0
    prev_last_run_xom = 0
    prev_last_run_daq = 0 
    try:
        last_run_xom = int(dbl.get_max(xomdatadb,"run_id"))
    except(IndexError):
        last_run_xom = 0    
    last_run_daq = dbl.get_max(rundb,"number")
    print("last_run_xom = ",last_run_xom) 
    ##############################################
    ### filling a list with analysis instances ###
    ##############################################
    analysis_list = []
    for analysis_name in analysis_names:
        an = getattr(analysismodule, analysis_name )(analysis_name)
        an.fill_from_config(xomconfig)
        analysis_list.append(an)
    if verbose:
        for an in analysis_list:
            an.printname()

    ##############################
    ### Starting the main loop ###
    ##############################
    while(a<1):
        time.sleep(1)
        # check for new runs in run DB
        last_run_daq = dbl.get_max(rundb,"number")
        
        if prev_last_run_daq==last_run_daq:
            logging.info('no new run')
            print("no new run")
            continue
        if last_run_daq > prev_last_run_daq:
            prev_last_run_daq  = last_run_daq
        
        # check if xom is up to date
        for an in analysis_list:
            try: 
                last_run_xom = dbl.get_max(xomdatadb,"run_id", query={"variable_name": an.variable_name})
            except(IndexError):
                if verbose:
                    print("new variable here")
                logging.info("new variable in xom")
                last_run_xom = 0
            try:
                if last_run_daq < last_run_xom:
                    raise ValueError
                elif last_run_daq == last_run_xom:
                    logging.info("nothing to do, analysis ?? up to date")
                    continue
                else:
                    print ("we should be here")
                    list_of_new_runs = list(range(last_run_xom +1, last_run_daq +1 ,1))
            except(ValueError):
                logging.error('xom run larger than last rundb run, exiting')
                print(f"last run of XOM ( = {last_run_xom}) is larger than last run of DAQ ( = {last_run_daq})...")
                print("Check xom data base, something is really wrong, will exit now")

            #produce list of runs according the analysis:
            list_of_command = an.produce_list_of_runs(list_of_new_runs)

            # write the command list in the text file
            for command in list_of_command:
                last_container = an.container_list[0]
                container_part = ' --container ' + last_container 
                total_command = constant.singularity_base + last_container + " " + command + '\n'
                
                #insure the file is not locked by other process:
                fd = ll.acquire(command_file, timeout=10)

                
                with open(command_file, 'a+') as f:
                    f.write(total_command)
                
                # unlock the txt file 
                ll.release(fd)



        



if __name__ == "__main__":
    main()












#    a = 1
# pprint.pprint(f'last run {last_run_daq}')
# pprint.pprint(f'last run xom {last_run_xom}')
# #print("xom data = ", xomdata.find_one())
    # coll = list(rundb.find({"number" : {"$in": [39321, 39323]}, "mode":"tpc_kr83m"},{'number':1}))
    # for x in coll:
    #     print(x)
        

#def last_run_check():



