#!/usr/bin/env python

import sys
from argparse import ArgumentParser
import json
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps

serveraddress = {'dali':"90.147.119.208",'lngs':"127.0.0.1"}

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



def UploadVariable(server='dali'):

    # Connecting to the XOM DB
    client = ConnectToDB(server)    

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    variables = database['variables']

    variables.delete_many({})

    variabledef = {}
    with open('variables.json','r') as f:
        variabledef = json.load(f)
        f.close()

    print (variabledef)
    # variable = {}
    # variable['name'] = 'lightyield'
    # variable['legend_name'] = 'Light Yield'
    # variable['unit'] = '[PE/KeV]'
    # variable['logy'] = False


    # Uploads data
    variables.insert_many(variabledef)


def UploadData(server='dali'):
    print('uploading data')
    # Connecting to the XOM DB
    client = ConnectToDB(server)

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    data = database['data']

    # Load data from json file
    dataset = LoadData('result.json')

    # Uploads data
    data.insert_many(dataset)

    

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

    parser = ArgumentParser("XomDB")

    parser.add_argument("server", nargs='?', type=str, default='dali', help="what server the script is run on, will change the address to connect for mongodb")
    parser.add_argument("--show", help="Shows informations and statistics about the database", action='store_true')
    parser.add_argument("--upload", help="Uploads data from a json file to XOM database", action='store_true')
    parser.add_argument("--upload_variable", help="Uploads the definition of a new variable in the XOM database", action='store_true')

    args = parser.parse_args()
    server = args.server
    if (args.show):
        ShowXomDB(server)
    if (args.upload):
        UploadData(server)
    if (args.upload_variable):
        UploadVariable(server)
    

if __name__ == "__main__":
    main()
