import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from utilix.config import Config
from bson.json_util import dumps
import json
import logging

rundb = pymongo_collection('runs')
# create logger
module_logger = logging.getLogger('proc_compare.analysis')

class Analysis:
    def __init__(self, name):
        self.variable_name = name
        self.container_list = []
        self.runwise = False
        self.command = ""
        self.logger = logging.getLogger('proc_compare.analysis.'+self.variable_name)
    
    def fill_from_config(self, xomconfig):

        containerlist = xomconfig.get(self.variable_name,'container')
        self.container_list = containerlist.split(',')
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
        run_min = 47500
 #       valid_runs = list(filter(lambda r: r > run_min == 0, list_of_runs) )
        valid_runs = list(filter(lambda r: r > run_min, list_of_runs) )
#        valid_runs_dict = list(rundb.find({"number" : {"$in": valid_runs}},{'number':1,'_id':0}))

#        valid_runs_dict = list(rundb.find({"number" : {"$in": valid_runs}, "mode":"tpc_bkg"},{'number':1,'_id':0}))
#        valid_runs = [list(valid_dict.values())[0] for valid_dict in valid_runs_dict]
#        valid_runs = list(filter(lambda r: r % 25 == 0, valid_runs))
        if valid_runs:
            for cont in self.container_list:
                valid_runs_str = str(valid_runs).strip('[]')
                self.logger.info('in cont %s, appending new command for runs: %s', cont, valid_runs_str)
                for r in valid_runs:
                    list_of_command.append(self.command.replace('[run]',str(r)) + " --container " + cont)
                
        else:
            print("no valid run analysis ", self.variable_name)
        return list_of_command
        

class test_var_2(Analysis):
    def produce_list_of_runs(self, list_of_runs):
        list_of_command = []
        # specific dummy conditions for test_var_2: 2 consecutive Kr runs
        run_min = 40000
        # find the kr83m runs within the new runs
        coll = list(rundb.find({"number" : {"$in": list_of_runs}, "mode":"background_linked"},{'number':1}))
        valid_runs = []
        [valid_runs.append(x['number']) for x in coll]
        valid_runs.sort()
        valid_runs = list(filter(lambda r: r > run_min, valid_runs) )
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
        for l in valid_run_lists[::10]: 
            for cont in self.container_list:
                list_of_command.append(self.command.replace('[runs]', " ".join(map(str,l)))  + " --container " + cont)
        if len(l) == 0:
            logging.info("no valid run this analysis")
        return list_of_command


class ly_qp(Analysis):
    def produce_list_of_runs(self, list_of_runs):
        list_of_command = []
        exclude_tags = ["messy","bad", "nonsr0_configuration", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "hot_spot","abandon"]
        exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]

        include_tags = [{"$regex":"_sr0"},"lt_24h_after_kr"]
        include_tags_query =  [{"tags.name": i} for i in include_tags]

        run_mode ='tpc_kr83m'
        coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode}))
        valid_runs = []
        [valid_runs.append(x['number']) for x in coll]
        print ("QP analysis: ", valid_runs)
        valid_runs.sort()
        valid_runs = list(filter(lambda r: r % 10 == 0, valid_runs))
        if valid_runs:
            for cont in self.container_list:
                for r in valid_runs:
                    list_of_command.append(self.command.replace('[run]',str(r)) + " --container " + cont)
        else:
            print("no valid run analysis ", self.variable_name)
        return list_of_command
        
        
        
        
        
    