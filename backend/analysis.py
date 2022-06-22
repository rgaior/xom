import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from utilix.config import Config
from bson.json_util import dumps
import json

rundb = pymongo_collection('runs')

class Analysis:
    def __init__(self, name):
        self.variable_name = name
        self.container_list = []
        self.runwise = False
        self.command = ""
    
    def fill_from_config(self, xomconfig):
        self.container_list =  json.loads(xomconfig.get(self.variable_name,'container'))
        self.runwise = xomconfig.getboolean(self.variable_name,'runwise')
        self.command = xomconfig.get(self.variable_name,'command')
    def printname(self):
        print(f"##### Variable: {self.variable_name} ##########")
        print("container list =", self.container_list)
        print("runwise = ", self.runwise)
        print("command =", self.command)
        print("###################################################")
    
class test_var_1(Analysis):
    def produce_list_of_runs(self,list_of_runs):
        list_of_command = []
        run_min = 40000
        valid_runs = list(filter(lambda r: r > run_min == 0, list_of_runs) )
        valid_runs = list(rundb.find({"number" : {"$in": valid_runs}, "mode":"tpc_bkg"},{'number':1}))
        valid_runs = list(filter(lambda r: r % 10 == 0, valid_runs))
        if valid_runs:
            for r in valid_runs:
                list_of_command.append(self.command.replace('[run]',str(r)) )  
        else:
            logging.info("no valid run this analysis")
        return list_of_command
        

class test_var_2(Analysis):
    def produce_list_of_runs(self, list_of_runs):
        list_of_command = []
        # specific dummy conditions for test_var_2: 2 consecutive Kr runs

        # find the kr83m runs within the new runs
        coll = list(rundb.find({"number" : {"$in": list_of_runs}, "mode":"tpc_kr83m"},{'number':1}))
        valid_runs = []
        [valid_runs.append(x['number']) for x in coll]
        valid_runs.sort()
        valid_run_lists = []
        run_size = len(valid_runs)
        skip = False
        for i, r in enumerate(valid_runs):                
            if skip == True:
                skip = False
                continue
            if i+1 < run_size:
                if (valid_runs[i+1] == r+1):
                    valid_run_lists.append([valid_runs[i],valid_runs[i+1]])
                    skip = True
        for l in valid_run_lists: 
            list_of_command.append(self.command.replace('[runs]', " ".join(map(str,l))) )
        if len(l) == 0:
            logging.info("no valid run this analysis")
        return list_of_command

    
        
        
        
        
        
    