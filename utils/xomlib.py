#!/usr/bin/env python

import sys
from argparse import ArgumentParser
import json
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import configparser

serveraddress = {'dali':"90.147.119.208",'lngs':"127.0.0.1"}

xomconfig = configparser.ConfigParser()
xomconfig.sections()
xomconfig.read('../utils/xomconfig.cfg')
def ConnectToDB(server):
    try:
        client = MongoClient(serveraddress[server], 27017)
    except:
        print('could not connect to the DB from  {} with address {} '.format(server, serveraddress[server]))

    return client

def LoadData(filename):
    dataset = {}
    with open(filename,'r') as f:
        dataset = json.load(f)
        f.close()
    return dataset

def SaveData(result,filename,mode='w'):
    with open(filename,mode) as f:
        json.dump(result,f)
        f.close()

def UploadVariable(variable_name, server='dali'):

    # Connecting to the XOM DB
    client = ConnectToDB(server)    

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    variables = database['variables']

    variables.delete_many({"variable_name":variable_name})
    variable = xomconfig._sections[variable_name]

    # Uploads data
    variables.insert_one(variable)


def UploadData(jsonfilename, server='dali'):
    print('uploading data')
    # Connecting to the XOM DB
    client = ConnectToDB(server)

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    data = database['data']

    # Load data from json file
    dataset = LoadData(jsonfilename)

    # Uploads data
    data.insert_many(dataset)


def UploadDataDict(dataset, server='dali'):
    print('uploading data')
    # Connecting to the XOM DB
    client = ConnectToDB(server)

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    data = database['data']

    print('dataset = ', dataset)
    # Uploads data
    data.insert_one(dataset)

    

def ShowXomDB(server='dali'):

    # Connecting to the XOM DB
    client = ConnectToDB(server)
    #client.server_info()

    # Getting the list of databases
    dbs = client.list_database_names()
    print("Available databases: ",dbs)

    # Accessing to XOM database
    database = client['xom']
    
    # Getting the list of collections
    collections = database.list_collection_names()
    print("Available collections: ",collections)

    # Dumps variables
    variables = database['variables']
    allvariables = variables.find({})
    
    for variable in allvariables:
        print(dumps(variable, indent=4))


    # Dumps data
    data = database['data']
    alldata = data.find({})
    
    for d in alldata:
        print(dumps(d, indent=4))
    
    

def main():
    print()
    print("--------------------------------------")
    print("XOMDB - Utilities for the XOM Database")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("xomlib")

    parser.add_argument("server", nargs='?', type=str, default='dali', help="what server the script is run on, will change the address to connect for mongodb")
    parser.add_argument("--show", help="Shows informations and statistics about the database", action='store_true')
    parser.add_argument("--upload", help="Uploads data from a json file to XOM database", action='store_true')
    
    parser.add_argument("--upload_variable", help="Uploads the definition of a new variable in the XOM database", action='store_true')
    parser.add_argument("--variable_name", type=str, help="Uploads the definition of a new variable in the XOM database")

    args = parser.parse_args()
    server = args.server
    if (args.show):
        ShowXomDB(server)
    if (args.upload):
        UploadData(server)
    if (args.upload_variable):
        UploadVariable(args.variable_name, server)
    

if __name__ == "__main__":
    main()
