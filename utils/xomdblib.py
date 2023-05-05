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
def connect_to_DB(database, server):
    if database == 'influxdb':
        try:
            client = influxdb_client.InfluxDBClient(
                url=info.url,
                token=info.token,
                org=info.org
            )   
        except:
            print('could not connect to the DB {} '.format(database) )
    elif database = 'mongodb':
        try:
            client == MongoClient(constant.serveraddress[server], 27017)
        except:
            print('could not connect to the DB from  {} with address {} '.format(server, constant.serveraddress[server]))
    return client

 
# rundb = pymongo_collection('runs')
# db_client = connect_to_DB('dali')
# xomdb = db_client['xom']

# Accessing to Data collection
xomvariablesdb = xomdb['variables']
xomdatadb = xomdb['data']


 
#def get_max_influxdb(client, variable_name, query=None):
def get_max(database, col, variable_name, query=None):
    '''either takes a mongodb collection or a client of influxdb'''
    if database == 'mongodb':
        try:
            if query:
                max = col.find(query).sort(name_of_variable,-1).limit(1)[0][name_of_variable]        
            else:
                max = col.find({}).sort(name_of_variable,-1).limit(1)[0][name_of_variable]
        except:
            print("error in get max")
    else:
        query_api = client.query_api()
        if query : 
            fluxquery = query
        else:
            fluxquery = 'from(bucket:"xom") |>  range(start: '+ -constant.query_period+ 'd) |> filter(fn: (r) => r.variable_name =='+ variable_name + ') |> sort(columns: ["runid"] ) '
        max = col.query_api(fluxquery)

    return max

def reset_xomdb(col = None):    
    col.delete_many({'run_id': {"$gt": 0}})

def find_one(col=None):
    if not col:
        col = xomdatadb
    print(col.find_one())


def latest(col):
    print(col.find().sort("_id",-1).limit(1)[0])

def main():
    print()
    print("--------------------------------------")
    print("XOM DB LIB - Utilities for the XOM Database")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("xomlib")

    parser.add_argument("server", nargs='?', type=str, default='dali', help="what server the script is run on, will change the address to connect for mongodb")    
    parser.add_argument("database", nargs='?', type=str, help="either mongodb or influxdb",action='store_true')
    parser.add_argument("collection", nargs='?', type=str, default='xom', help="what server the script is run on, will change the address to connect for mongodb")    
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
