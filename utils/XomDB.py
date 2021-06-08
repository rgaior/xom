#!/usr/bin/env python

import sys
from argparse import ArgumentParser
import json
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps

def FillCollection():

    # Connecting to the XOM DB
    client = MongoClient( "90.147.119.208", 27017)

    # Accessing to XOM database
    xom = client['xom']
    

def ShowXomDB():

    # Connecting to the XOM DB
    client = MongoClient( "90.147.119.208", 27017)
    #client.server_info()

    # Getting the list of databases
    dbs = client.list_database_names()
    print("Available databases: ",dbs)

    # Accessing to XOM database
    xom = client['xom']
    
    # Getting the list of collections
    collections = xom.list_collection_names()
    print("Available collections: ",collections)

    collection = xom['v1.0']
    data = collection.find({})
    
    for d in data:
        print(dumps(d, indent=4))
    
    

def main():
    print()
    print("--------------------------------------")
    print("XOMDB - Utilities for the XOM Database")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("XomDB")

    parser.add_argument("--show", help="Shows informations and statistics about the database", action='store_true')

    args = parser.parse_args()

    if (args.show):
        ShowXomDB()

#    CreateCollection()

if __name__ == "__main__":
    main()
