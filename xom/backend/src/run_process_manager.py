import os
import sys
import time
import hashlib
import json
import random
import requests
import signal
import socket
import subprocess
import traceback
import datetime
import logging
from datetime import timedelta
import tarfile
import copy
import shutil
import tempfile
import io
import locale
import json
import pymongo
import argparse
import numpy as np 
import pandas as pd
from tqdm import tqdm
from glob import glob
import pickle
import hax
from hax import cuts
from pax import configuration, units, datastructure
from manage_processes_v0 import ProcessManager


shutil.rmtree("/home/mlotfi/.cache/rootpy")
for f in glob("pax_*"):
    os.remove(f)
#!rm -f pax_*
dirname = '/home/mlotfi/.cache/rootpy/x86_64-60403/dicts/'


if not os.path.exists(dirname):
    os.makedirs(dirname)


minitree_folder = sys.argv[1]

def create_delete_folder(outputFolder, createFolder=True):
        """ Create a new folder for every run, and every monitored variable
        - One json file will be dumped into this directory
        - One png figure will be dumped into this directory as well
        - This whole directory will be copied over SCP to Gran Sasso
        - A directory is going to be created, that has the name of run number, subdirectories: for each monitored observable
        - The default is: createFolder = True, if you set it to "0" or False the same directory will be deleted again.
        """
        #directory name should have the runid, source and finally variables
        
        cwd_variable = outputFolder 
        # now lets create this cwd_full
        if createFolder:
            try:  
                os.makedirs(outputFolder)
            except OSError:  
                print ("Creation of the directory %s failed" % outputFolder)
            else:  
                print ("Successfully created the directory %s" % outputFolder)
        # Now lets delete
        else:
            if os.path.exists(outputFolder):
                try:
                    os.rmdir(outputFolder)
                except OSError:  
                    print ("Deletion of the directory %s failed" % outputFolder)
                else:  
                    print ("Successfully deleted the directory %s" % outputFolder)


#def get_data_hax(run_number, pax_version):
#    """
#    we assume that the data are in the directory
#    /project2/lgrandi/xenon1t/minitrees
#    This function uses hax to extract the data frames assuming a pax_version: in this case pax_version 6.8.0
#    """
#    # initialize hax using the directory for the minitrees and pax_version
#    hax.init(experiment='XENON1T', minitree_paths =['/project2/lgrandi/xenon1t/minitrees/%s/'%pax_version],\
#                 main_data_paths=['/project2/lgrandi/xenon1t/processed/%s/'%pax_version],\
#                 detector='tpc')
#    return hax.minitrees.load([run_number],["CorrectedDoubleS1Scatter","Basics", "Fundamentals"])

def getKrCalibration(rc_days = 1):
    """
    it queries the RunDB for Kr data for a number of days from today to the past by rc_days
    """
    #This function interacts with the XENON1T runDB:
    uri = 'mongodb://pax:%s@copslx50.fysik.su.se:27017/run'
    uri = uri % os.environ.get('MONGO_PASSWORD')
    client = pymongo.MongoClient(uri, replicaSet='runs', readPreference='secondaryPreferred')
    

    
    db = client['run']
    collection = db['runs_new']
    
    #Create a query of the recent days (rc_days)
    # -for all Kr data for the last 360 days
    
    dt_today = datetime.datetime.today()
    dt_recent = timedelta(days=rc_days)
    dt_begin = dt_today - dt_recent
    #for debug 
    dt_begin  = datetime.datetime(2017, 11, 30, 0, 0)
    dt_end    = datetime.datetime(2018,3,1,0,0)
    
    query =  {"source.type": "Kr83m", "start": {'$gt': dt_begin}, "end":{"$lt":dt_end}}#, "tags.name": "_sciencerun1"}#, "tags.name": "_sciencerun0"}

    cursor = list( collection.find(query) ) # make a list of the results of the querry

    #get the version of pax    
        
    run_dbtags = []
    for i_c in cursor:
        run_number = i_c['number']
        run_name  = i_c['name']
        run_start = i_c['start']
        run_end   = i_c['end']
        run_source = None
        versions_pax = list()
        if "data" in i_c.keys():

            for d in i_c["data"]:
                if "pax_version" in d.keys():
                    versions_pax.append(d["pax_version"])
                    
                else:
                    print("are we skipping it?", run_name,run_number)
                    continue
        if len(versions_pax) == 0: ### this means that these files are problematic
            continue
        
        pax_version = "pax_%s" % (versions_pax[-1])
        TagFile = False
        if 'tags' in i_c.keys() and len(i_c['tags']) > 0:            
            for itagdict in i_c['tags']:
                for v in itagdict.values():
                    if (isinstance(v,str)) and (v in ["bad","messy","_blinded"]): 
                        print("this run must be bad: ", run_name, v)
                        TagFile = True
                        break

        if not TagFile:
        
            run_dbtags.append((run_number, run_name, pax_version))

    return run_dbtags



runs_pax_versions = getKrCalibration(rc_days = 360)

run_data = dict()

print("we are going to analyse these files: ", len(runs_pax_versions))

for r in runs_pax_versions:
    start_time = time.clock()
    print("we are processing:", r[1])
    # initiate the process manager for each run, we know a priori 
    process_manager = ProcessManager(r[0], minitree_folder)
    original_directory  =  os.getcwd()
    data_directory  = process_manager.outputFolder
    
    #Now lets create the directory to store the data
    create_delete_folder(data_directory, createFolder=True)
    # Once it is created, lets get into it
    os.chdir(data_directory)
    # now lets start the process manger
    process_manager.process()
    #now write json file and png file here
    process_manager.write_json_file()
    # Check the existence of the json and png files
    # I will skip this part
    
    # lets copy: scp the whole directory to Gran Sasso
    # This step I need to skip for the moment
    
    # now lets go back to the original directory: where algorithms are
    os.chdir(original_directory)
    
    print ("20 -/-")
    print(time.clock() - start_time, "seconds")
    print("20 -/-")
    
#pickle.dump(run_data, open( "all_krypton_data", "wb" ) )
