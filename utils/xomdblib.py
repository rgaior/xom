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
from argparse import ArgumentParser


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
def get_max(name_of_variable,query=None):
    if not col:
        col = xomdatadb
    if query:
        max = col.find(query).sort(name_of_variable,-1).limit(1)[0][name_of_variable]        
    else:
        max = col.find().sort(name_of_variable,-1).limit(1)[0][name_of_variable]
    
    return max

def reset_xomdb(col =None):
    if not col:
        col = xomdatadb
    col.delete_many({'run_id': {"$gt": 0}})


def find_one(col=None):
    if not col:
        col = xomdatadb
    print(col.find_one())


def latest(col=None):
    if not col:
        col = xomdatadb
    print(col.find().sort("_id",-1).limit(1)[0])

def main():
    print()
    print("--------------------------------------")
    print("XOM DB LIB - Utilities for the XOM Database")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("xomlib")

    parser.add_argument("server", nargs='?', type=str, default='dali', help="what server the script is run on, will change the address to connect for mongodb")    
    parser.add_argument("--reset",  help="reset database, only for test purposes",action='store_true')
    parser.add_argument("--find_one", help="just showing one item",action='store_true')
    parser.add_argument("--latest", help="showing the latest item",action='store_true')

    args = parser.parse_args()
    server = args.server
    if (args.reset):
        reset_xomdb()
    if (args.latest):
        latest()
    if (args.find_one):
        find_one()
if __name__ == "__main__":
    main()