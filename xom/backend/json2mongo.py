import sys
import os
import json
import pymongo
from pymongo import MongoClient
import gridfs
from glob import glob

class WriteToDataBase():
    """
    this class is responsible for:
    1) reading the json files and dump them into the database
    2) saving the figures into the database as well
    it has two main functions:
    1) The first one that clears the database, it means you delete all documents and files that are in the database
    2) The second it saves the figures to the database and dump the json files into the database
    """
    def __init__(self, datapath=None,  database=None, collection=None, runnumber=None, jsonfile=None):

        self.jsonfile = jsonfile
        self.datapath    = datapath
        self.database_name   = database
        self.collection_name = collection
        self.run_number = runnumber
        self.client = MongoClient( "localhost", 27017, serverSelectionTimeoutMS=30 )  # 30 sec is the default time
        self.client.server_info()  # force connection on a request

        # get data from json file
        try:
            with open( self.jsonfile, "r" ) as jfile:
                self.data = json.load( jfile )
        except Exception as err:
            print( "the json file is empty or has problems" )
            print( err )
        # get the data base and create the collection if it does not exist already
        try:
            assert isinstance( self.database_name, str )
            self.db = self.client[self.database_name]
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print( "the data base server is down" )
            print( err )

        assert isinstance( self.collection_name, str )
        if self.collection_name not in self.db.collection_names():
            self.collection = self.db.create_collection(self.collection_name)
        else:
            self.collection = self.db[self.collection_name]



    def modify_jsonfile(self):
        """
        Add the absolute path of the figures into the dictionaries
        it will be something like: /home/xom/data/xom/context_number/run_number/
        :name json file: to be dumped into the data base

        :return: new json file
        """
        # The json file has two keys: info and processes
        #we loop over all processes and we change the value of the key figure
        for proc in self.data["processes"].keys():
            for keys in self.data["processes"][proc].keys():
                if keys == "figure":
                    old_value = self.data["processes"][proc]["figure"]
                    new_value = self.datapath + "/" + old_value
                    self.data["processes"][proc]["figure"] = new_value
        #now we can re-write the modified dict to the json file
        try:
            with open( self.jsonfile, "w" ) as jfile:
                json.dump( self.data, jfile )
        except Exception as err:
            print("we could not write out the modified json file", err)
         return 0
        
    def write_to_db( self ) :
        
        """
        read the json files and write them as Documents into the database

        """
        # Check the existence of the current json file inside the data base
        # the name of the json file starts with run_number as: run_number.json
        try:
            for document in self.collection.find():
                # if the document with the given run number exists, delete it and re-write
                    if document["info"]["run"] == int( self.jsonfile.rstrip( ".json" ) ):
                        print( "File %s already in database" % document["info"]["filename"] )
                        self.collection.delete_one( {"info": self.data["info"]} )
                        self.collection.insert_one( self.data )
                    else:
                        self.collection.insert_one( self.data )

        except pymongo.errors.ServerSelectionTimeoutError as err:
            print("the data base server is down")
            print(err)
            sys.exit("check the database server if it is up and running ?")

        return 0
