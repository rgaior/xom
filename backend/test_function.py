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
import analysis 
analysismodule = importlib.import_module("analysis")  

rundb = pymongo_collection('runs')


def get_xom_config(configname='xomconfig.cfg'):
    xomconfig = configparser.ConfigParser()
    xomconfig.sections()
    configfilename = configname
    xomconfig.read('../utils/' + configfilename)
    return xomconfig

def check_jobs(job_limit):
    command =  "squeue -u gaior | wc --lines"
    execcommand = shlex.split(command)
    process = subprocess.run(execcommand,
                                         stdout=subprocess.PIPE,
                                         universal_newlines=True)
    nr_of_lines = int(process.result)
    print(nr_of_lines)
    if  nr_of_lines> job_limit:
        return False
    else:
        return True


def main():
    print()
    print("--------------------------------------")
    print("TEST FUNCTION for BACKEND    ")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("test_function")
    parser.add_argument("--config", help="test the config", action='store_true')
    parser.add_argument("--rundb", help="test the rundb functions", action='store_true')
    parser.add_argument("--xomdb", help="test the xomdb functions", action='store_true')
    parser.add_argument("--jobs", help="test the xomdb functions", action='store_true')
    parser.add_argument("--verbose", help="Shows informations and statistics about the database", action='store_true')
    args = parser.parse_args()
    verbose = args.verbose

    # connect to the Xenon run database
#    rundb = dbl.connect_to_DAQ_DB('runs')
 
    type_of_db = constant.type_of_db
    xomdb = dbl.Xomdb(type_of_db,"measurementxom")


    if args.config:
        #############################
        ### sets up the xomconfig ###
        #############################
        xomconfig = get_xom_config(constant.configname)
        analysis_names = xomconfig.sections()
        print("##########################################" )
        print("Reading the config file: ",xomconfig)
        print("##########################################\n" )
        analysis_list = []
        for analysis_name in analysis_names:
            an = analysis.Analysis(analysis_name)
#getattr(analysismodule, analysis_name)(analysis_name)
#            an = getattr(analysismodule, analysis_name )(analysis_name)
            an.fill_from_config(xomconfig)
            analysis_list.append(an)
        for an in analysis_list:
            an.print_config()

        
    if args.rundb:
#        last_run_daq = dbl.get_max_mongodb(rundb, "number")

        #exclude_tags = ["messy","bad", "nonsr0_configuration", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "warm_spot","abandon"]
#        include_tags = ["_sr1_preliminary"]
        exclude_tags = []
        include_tags = []
 
        if not exclude_tags:
#            exclude_tags_query = [{"tags.name":{"$ne": ""}}]
            exclude_tags_query = [{}]
        else:
            exclude_tags_query = [{"tags.name":{"$ne": e}} for  e in exclude_tags]

        if not include_tags:
#            include_tags_query = {"tags.name":{"$all": ""}}
            include_tags_query = [{}]
        else:
            include_tags_query =  [{"tags.name": i} for i in include_tags]
            
        # exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]
        # print('exclude_tags_query = ', exclude_tags_query)
        # include_tags = ["_sr1_preliminary"]
#        run_mode = 'tpc_kr83m'
        run_mode = ''
        #        include_tags = [""]
        if not run_mode:
            run_mode_query = {"$ne":  " "}
        else:             
            run_mode_query = run_mode
#            run_mode_query = {"$e" + run_mode}

#        coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode, "number": {"$gt":52000} }))
        coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode_query, "number": {"$gt":52000} }))
        #        coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode}))
#        coll = list(rundb.find({"number": {"$gt":52000} }))
#        print(coll)
# "$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode}))
        valid_runs = []
        [valid_runs.append(x['number']) for x in coll]
        print ("QP analysis: ", valid_runs)

        print("latest entry in DAQ = ",last_run_daq) 




    if args.xomdb:
        last_run_xom = xomdb.get_last_runid()
        print("latest entry in xom = ",last_run_xom) 
        last_run_xomv1 = xomdb.get_last_runid_from_var("temp_v1")
        print("latest entry in xom for temp_v1 = ",last_run_xomv1) 
        last_run_xomv2 = xomdb.get_last_runid_from_var("temp_v2")
        print("latest entry in xom for temp_v2 = ",last_run_xomv2) 
        
    if args.jobs:
        check_jobs(3)

    if args.data:
        include_tags = ['_sr1_preliminary']
        exclude_tags = ['messy','bad', 'nonsr0_configuration', 'ramp down',  'ramp up',  'ramp_down', 'ramp_up', 'hot_spot','abandon']
        available_type = ['event_basics', 'peak_basics']

        allruns = st.select_runs(available=available_type,
                                 exclude_tags=exclude_tags,
                                 include_tags=include_tags,)
        print("result of select run", allruns)
        
        print(st.is_stored(run_id, 'event_basics')) 
        print(st.is_stored(run_id, 'peak_basics'))


        check_jobs(3)



    # a = 0

    # prev_last_run_xom = 0
    # prev_last_run_daq = 0 
    # try:
    #     last_run_xom = int(dbl.get_max("run_id",xomdatadb))
    # except(IndexError):
    #     last_run_xom = 0    
    #     print("latest entry in XOM DB = ",last_run_xom)  

    # ##############################################
    # ### filling a list with analysis instances ###
    # ##############################################
    # analysis_list = []
    # for analysis_name in analysis_names:
    #     an = getattr(analysismodule, analysis_name )(analysis_name)
    #     an.fill_from_config(xomconfig)
    #     analysis_list.append(an)
    # if verbose:
    #     for an in analysis_list:
    #         an.printname()

    # ##############################
    # ### Starting the main loop ###
    # ##############################
    # while(a<1):
    #     # check for new runs in run DB
    #     last_run_daq = dbl.get_max("number", rundb)
        
    #     if prev_last_run_daq==last_run_daq:
    #         logger.info('no new run')
    #         print("no new run")
    #         continue
    #     if last_run_daq > prev_last_run_daq:
    #         prev_last_run_daq  = last_run_daq
        
    #     # check if xom is up to date
    #     for an in analysis_list:
    #         try: 
    #             last_run_xom = dbl.get_max("run_id",xomdatadb,query={"var_name": an.variable_name})
    #         except(IndexError):
    #             if verbose:
    #                 print("new variable here")
    #             logger.info("new variable in xom")
    #             last_run_xom = 0
    #         # 
    #         try:
    #             if last_run_daq < last_run_xom:
    #                 raise ValueError
    #             elif last_run_daq == last_run_xom:
    #                 logger.info("nothing to do, analysis %s up to date", an.variable_name)
    #                 continue
    #             else:
    #                 list_of_new_runs = list(range(last_run_xom +1, last_run_daq +1 ,1))
    #         except(ValueError):
    #             logger.error('xom run larger than last rundb run, exiting')
    #             print(f"last run of XOM ( = {last_run_xom}) is larger than last run of DAQ ( = {last_run_daq})...")
    #             print("Check xom data base, something is really wrong, will exit now")

    #         #produce list of runs according the analysis:
    #         list_of_command = an.produce_list_of_runs(list_of_new_runs)

    #         # # write the command list in the text file
    #         # for command in list_of_command:
    #         #     container = command.split()[-1]
    #         #     total_command = constant.singularity_base + container + " " + command + '\n'
    #         #     #insure the file is not locked by other process:
    #         #     fd = ll.acquire(command_file, timeout=10)
    #         #     with open(command_file, 'a+') as f:
    #         #         f.write(total_command)
                
    #         #     # unlock the txt file 
    #         #     ll.release(fd)

    #     time.sleep(constant.exec_period)
    

        



if __name__ == "__main__":
    main()







 




# #    a = 1
# # pprint.pprint(f'last run {last_run_daq}')
# # pprint.pprint(f'last run xom {last_run_xom}')
# # #print("xom data = ", xomdata.find_one())
#     # coll = list(rundb.find({"number" : {"$in": [39321, 39323]}, "mode":"tpc_kr83m"},{'number':1}))
#     # for x in coll:
#     #     print(x)
        

# #def last_run_check():



