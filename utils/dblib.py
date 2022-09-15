#!/usr/bin/env python
import os
import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from utilix.config import Config
import sys
import pprint 
import numpy as np
import time
import constant

########################
### connection to DB ###
########################
def connect_to_DB(server):
    try:
        client = MongoClient(constant.serveraddress[server], 27017)
    except:
        print('could not connect to the DB from  {} with address {} '.format(server, constant.serveraddress[server]))
    return client


rundb = pymongo_collection('runs')
db_client = connect_to_DB('dali')
xomdb = db_client['xom']

# Accessing to Data collection
xomvariablesdb = xomdb['variables']
xomdatadb = xomdb['data']
def get_max(col,name_of_variable,query=None):
    if query:
        max = col.find(query).sort(name_of_variable,-1).limit(1)[0][name_of_variable]        
    else:
        max = col.find().sort(name_of_variable,-1).limit(1)[0][name_of_variable]
    
    return max