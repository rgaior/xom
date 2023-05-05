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
import analysis as analysis
#analysismodule = importlib.import_module("analysis")  

import logging
from logging.handlers import TimedRotatingFileHandler
logger = logging.getLogger('proc_compare')
log_format = "%(asctime)s  - %(name)s - %(levelname)s - %(message)s"
log_level = 10
handler = TimedRotatingFileHandler('../logs/proc_compare.log', when="midnight", interval=1)
logger.setLevel(log_level)
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
# add a suffix which you want
handler.suffix = "%Y%m%d"
# finally add handler to logger    
logger.addHandler(handler)
import glob

import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from utilix.config import Config

def connect_to_DAQ_DB(collection='runs'):
    rundb = pymongo_collection(collection)
    return rundb


def get_last_runid(col,name_of_variable,query=None):
    '''written only for the mongo db case '''
    if query:
        max = col.find(query).sort(name_of_variable,-1).limit(1)[0][name_of_variable]        
    else:
        max = col.find().sort(name_of_variable,-1).limit(1)[0][name_of_variable]    
    return max

def get_max_mongodb(col,name_of_variable,query=None):
    if query:
        max = col.find(query).sort(name_of_variable,-1).limit(1)[0][name_of_variable]        
    else:
        max = col.find().sort(name_of_variable,-1).limit(1)[0][name_of_variable]    
    return max

def get_xom_config(configname='xomconfig.cfg'):
    xomconfig = configparser.ConfigParser()
    xomconfig.sections()
    configfilename = configname
    xomconfig.read('../utils/' + configfilename)
    return xomconfig


def process_command(command):
    execcommand = shlex.split(command)
    print(execcommand)
    process = subprocess.run(execcommand,
                             stdout=subprocess.PIPE,
                             universal_newlines=True)


def remove_file(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def empty_directory(path):
    for i in glob.glob(os.path.join(path, '*')):
        remove_file(i)



def main():
    print()
    print("--------------------------------------")
    print("XOM BACKEND PROCESS COMPARE module    ")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("proc_compare")
    parser.add_argument("--verbose", help="Shows informations and statistics about the database", action='store_true')
    parser.add_argument("--clean", help="clean the measurements : data, todo, done, to be used in test phase only", action='store_true')
    parser.add_argument("--loglevel", type=str, help="Shows informations and statistics about the database", default='INFO')
    args = parser.parse_args()
    verbose = args.verbose
    clean = args.clean
    loglevel = args.loglevel
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(loglevel.upper())
    # create formatter and add it to the handlers
    formatterch = logging.Formatter('%(name)-20s - %(levelname)-5s - %(message)s')
    ch.setFormatter(formatterch)
    # add the handlers to the logger
    logger.addHandler(ch)

    
        
    # text file where all the command to be executed will be written 
    command_file = 'list_of_commands.txt'
    
    # connect to the Xenon run database
    logger.info('connecting to DAQ dbs')
    rundb = connect_to_DAQ_DB('runs')

    # conncet to xom database
    logger.info('connecting to xom dbs')
    type_of_db = constant.type_of_db
    xomdb = dbl.Xomdb(type_of_db,"xomdata")
    xomdbtodo = dbl.Xomdb(type_of_db,"xomtodo")
    xomdbdone = dbl.Xomdb(type_of_db,"xomdone")
    xomdbsubmitted = dbl.Xomdb(type_of_db,"xomsubmitted")
    

    if clean:
        xomdb.delete()
        xomdbtodo.delete()
        xomdbdone.delete()
        xomdbsubmitted.delete()

        # here erase the job files
        empty_directory(constant.job_folder)
        logger.warning("delete all the measurement related to XOM")
    
    #############################
    ### sets up the xomconfig ###
    #############################
    xomconfig = get_xom_config(constant.configname)
    logger.info('set up config with file %s: ', constant.configname)
    analysis_names = xomconfig.sections()
    
    ##############################################
    ### filling a list with analysis instances ###
    ##############################################
    analysis_list = []
    for analysis_name in analysis_names:
        an = analysis.Analysis(analysis_name)
#getattr(analysismodule, analysis_name)(analysis_name)
        print (an.analysis_name)
        an.fill_from_config(xomconfig)
        analysis_list.append(an)
        # check if analysis exists in xom db
        xomdb.get_last_runid_from_analysis(analysis_name)
        if verbose:
            for an in analysis_list:
                an.print_config()


    stop_condition = 0

    prev_last_run_xom = 0
    prev_last_run_daq = 0 

    last_run_xom = int(xomdb.get_last_runid())
    last_run_daq = get_last_runid(rundb,"number")
    print("latest entry in DAQ = ",last_run_daq) 
    print("latest entry in XOM DB = ",last_run_xom)  

 
    ##############################
    ### Starting the main loop ###
    ##############################
    while(stop_condition<1):
        # check for new runs in run DB
        last_run_daq = get_last_runid(rundb,"number")
        
        if prev_last_run_daq==last_run_daq:
            logger.info('no DAQ new run')
            time.sleep(10*constant.exec_period)
            continue
        if last_run_daq > prev_last_run_daq:
            prev_last_run_daq  = last_run_daq
            
        # check if xom is up to date
        for an in analysis_list:
            # need to be already presnent in the data base
            last_todo_xom = xomdbtodo.get_last_runid_from_analysis(an.analysis_name)
            last_done_xom = xomdbdone.get_last_runid_from_analysis(an.analysis_name)
            logger.debug(f"last_todo_xom = {last_todo_xom} last_done_xom = {last_done_xom}")
            last_xom = max([last_todo_xom,last_done_xom])
            if last_run_daq == last_xom:
                    logger.info("nothing to write in todo dB, analysis %s up to date", an.analysis_name)
                    continue
            else:
                #produce list of runs according the analysis:
                logger.info(f"producing the list of new runs from runid {last_todo_xom } to runid {last_run_daq }") 
#                list_of_new_runs = list(range(last_todo_xom +1, last_run_daq +1 ,1))
                list_of_command = an.produce_list_of_runs(last_xom, last_run_daq)
                
        time.sleep(constant.exec_period)

if __name__ == "__main__":
    main()
