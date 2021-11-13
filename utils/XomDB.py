#!/usr/bin/env python

import sys
from argparse import ArgumentParser
import json
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps

def LoadData(filename):
    dataset = {}
    with open(filename,'r') as f:
        dataset = json.load(f)
        f.close()
    return dataset



def UploadVariable():

    # Connecting to the XOM DB
    client = MongoClient( "90.147.119.208", 27017)

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    variables = database['variables']

    variable = {}
    variable['name'] = 'lightyield'
    variable['legend_name'] = 'Light Yield'
    variable['unit'] = '[PE/KeV]'
    variable['logy'] = False


    # Uploads data
    variables.insert_many([variable])


def UploadData():

    # Connecting to the XOM DB
    client = MongoClient( "90.147.119.208", 27017)

    # Accessing to XOM database
    database = client['xom']

    # Accessing to Data collection
    data = database['data']

    # Load data from json file
    dataset = LoadData('result.json')

    # Uploads data
    data.insert_many(dataset)

    

def ShowXomDB():

    # Connecting to the XOM DB
    client = MongoClient( "90.147.119.208", 27017)
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

    parser.add_argument("--show", help="Shows informations and statistics about the database", action='store_true')
    parser.add_argument("--upload", help="Uploads data from a json file to XOM database", action='store_true')
    parser.add_argument("--upload_variable", help="Uploads the definition of a new variable in the XOM database", action='store_true')

    args = parser.parse_args()

    if (args.show):
        ShowXomDB()
    if (args.upload):
        UploadData()
    if (args.upload_variable):
        UploadVariable()


if __name__ == "__main__":
    main()
