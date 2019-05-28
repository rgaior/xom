import os
import sys
import re
import numpy as np
import json
import pandas as pd
import pprint
from datetime import datetime
#import pm
from configparser import ConfigParser
import logging
log=logging.getLogger('pm')


#import of the classes necessary
from get_dataframes import GetDataFrame
from electron_life_time_v0 import ElectronLifetime
from light_yield_v0 import LightYield
from charge_yield_v1 import ChargeYield

### This is temporary: it needs to go to pm.init to be able to get it directly from there
print("THIS SHOULD BE CHANGED IN THE NEAR FUTURE: USE list_minitrees INSIDE the ini FILE")
list_minitrees = {}
list_minitrees["Kr83m"] = ["CorrectedDoubleS1Scatter"]

class ProcessManager:

    def __init__(self, runID, inputFolder, pax_version="pax_v6.8.0", dataType = "calibration", source="Kr83m"):
        
        self.run_id = runID
        self.inputFolder = inputFolder
        #self.outputFolder = outputFolder
        self.pax_version = pax_version
        # get the dataframe from pax, make use of the class GetDataFrame

        dataFrame = GetDataFrame(run_number = self.run_id, minitree_name= list_minitrees[source][0],\
                                 pax_version = self.pax_version, directory = self.inputFolder) 
        self.df = dataFrame.get_df() 
        
        self.timeInterval = 60*1e9 # one minute interval
        self.processes = {}
        self.info = {}
        self.data_type = dataType
        self.source  = source


        self.jsonFileName = str(self.run_id) + ".json"

        entries = len(self.df)
        if entries == 0:
            print ("The file you have provided has no entries ")
            ##HERE WE NEED TO RETURN AN EMPTY JSON FILE TO BE CONSISTENT
            ## WITH THE FRONT END
            sys.exit(0)
        log.info("Processing: %s with %d events" %( self.run_id, entries ))
        # outputFolder
        self.outputFolder =  os.getcwd() + "/" + str(self.run_id) + "/" + self.data_type + "/" + self.source

        
    
            
    def write_json_file(self):
        """
        dumping of the results to the json file

        """
        #first start with the runid as an info
        # run fill_info to initiate the infos that needs to be dumped into the Json file
        self.fill_info()

        #jsonName = pm.config['pm']['json_data_path'] +'/' + self.jsonFileName
        
        mergedDict = self.info.copy()
        #if isinstance(self.info, dict):
        #    mergedDict.update(self.rates)
        if isinstance(self.processes, dict):
            mergedDict.update(self.processes)
        pp = pprint.PrettyPrinter(indent=2)
        print("the json file: %s  is being writen "% self.jsonFileName)
        with open(self.jsonFileName , "w") as f:
            json.dump(mergedDict, f)
        pp.pprint(mergedDict)
        return 0


    def get_file_time_info(self):
        """
        get the initial time and end time of a file
        """
        return { "start_time":int(self.df["event_time"].min()),"end_time":int(self.df["event_time"].max()) }


    def fill_info(self):

        #self.info.setdefault('info',{}).update({'filename' : self.filename})
        self.info.setdefault('info',{}).update({'run' : int(self.run_id)})

        fileTimeInfo = self.get_file_time_info()
        
        self.info.setdefault('info',{}).update(fileTimeInfo)
        self.info.setdefault('info',{}).update({'offline production time' : \
                                                int((datetime.now()-datetime(1970,1,1)).total_seconds()*1.e9)})
        #self.info.setdefault('info',{}).update({'user' : os.getlogin()})
        self.info.setdefault('info',{}).update({'original entries' : \
                                                len(self.df['event_number'])})
        self.info.setdefault('info',{}).update({'pax version' : \
                                                self.pax_version })

        self.info.setdefault('info',{}).update({'type' : \
                                                self.data_type})
        self.info.setdefault('info',{}).update({'source' : \
                                                self.source})
        #try:
        #    self.info.setdefault('info',{}).update({'gimp_mode' : \
                                                    #self.rundb_info['reader']['ini']['gimp_mode']})
        #except:
         #   self.info.setdefault('info',{}).update({'gimp_mode' : 0})

        #self.info.setdefault('info',{}).update({'pm_config' : pm.config})

    


    def process(self):
        """ Here comes the processes, EL, LY"""
        
        #directory = pm.config['pm']['figs_path']
        #directory = "/Users/mlb20/xenon/pm/algorithms/fullmoni"
        pp = pprint.PrettyPrinter(indent=4)
        #outputFileName = directory + \
        #                 self.filename.rsplit(".",1)[0] + \
        #                 "_el_lifetime.png"


        if self.data_type == "calibration":
            if self.source == "Kr83m":
                #outputFileName = directory + \
                #         self.filename.rsplit(".",1)[0] + \
                #         "_el_lifetime.png"
                outputFileName = str(self.run_id) + "_el_lifetime.png"
                # Initialize the electron life time class
                el_lifetime = ElectronLifetime(self.df, outputFileName, source = "kr")
                # Get the electron life time
                result = el_lifetime.get_electron_lifetime()
                pp.pprint(result)

                if isinstance(result, dict):
                    self.processes.setdefault('processes',{}).update(result)
            
                else:
                    ##We need to add an empty json file not to crash the monitoring with stupid data.
                    log.warning("Failed to get the electron lifetime")
                    
                #Get the light yield
                print("The light yield for Kr: 32keV line is ongoing")
                #outputFileName = directory + \
                #         self.filename.rsplit(".",1)[0] + \
                #         "_32kev_light_yield.png"
                outputFileName =   str(self.run_id) + "_32kev_light_yield.png"
                
                light_yield_1 = LightYield("cs1_a", 32., self.df)
                result  = light_yield_1.get_light_yield(outputFileName)
                pp.pprint(result)
                
                if isinstance(result, dict):
                    self.processes.setdefault('processes',{}).update(result)
            
                else:
                    ##We need to add an empty json file not to crash the monitoring with stupid data.
                    log.warning("Failed to get the Light Yield for 32keV line")

                    
                print("The light yield for Kr: 9keV line is ongoing")

                #outputFileName = directory + \
                #         self.filename.rsplit(".",1)[0] + \
                #         "_9kev_light_yield.png"
                outputFileName =  str(self.run_id) + "_9kev_light_yield.png"
                light_yield_2 = LightYield("cs1_b", 9., self.df)

                result  = light_yield_1.get_light_yield(outputFileName)
                pp.pprint(result)
                #check the results, it should be all fine because all exceptions are taken care of inside LightYield class
                if isinstance(result, dict):
                    self.processes.setdefault('processes',{}).update(result)
            
                else:
                    ##We need to add an empty json file not to crash the monitoring with stupid data.
                    log.warning("Failed to get the Light Yield for 9keV line")

                #now let me get the Charge Yield
                print("the charge yield for Kr source is calculated for the sum of both gammas: 41keV")
                #outputFileName = directory + \
                #                 self.filename.rsplit(".",1)[0] + \
                #                 "_41keV_charge_yield.png"
                outputFileName = str(self.run_id) + "_41keV_charge_yield.png"
                
                charge_yield = ChargeYield("cs2_a_bottom", 41, self.df)


                #here 5 is the number of bins in time where to  look for the Charge Yield
                result = charge_yield.get_charge_yield(outputFileName, 5)
                pp.pprint(result)
                
                if isinstance(result, dict):
                    self.processes.setdefault('processes',{}).update(result)
            
                else:
                    log.warning("Failed to get the Charge Yield line")
