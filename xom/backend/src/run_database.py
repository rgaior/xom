import os
import time
import hashlib
import json
import random
import requests
import signal
import socket
import subprocess
import sys
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
    
    print("we are processing:", r[1])
    start_time = time.clock()
    run_data[r[0]] = get_data_hax(r[0], r[2]) 
    print (time.clock() - start_time, "seconds")
    
pickle.dump(run_data, open( "all_krypton_data", "wb" ) )
