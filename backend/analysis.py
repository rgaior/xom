import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from utilix.config import Config
from bson.json_util import dumps
import json
import logging
import sys
rundb = pymongo_collection('runs')
sys.path +=['../utils/']
import xomlib 
import dblib as dbl

import time
import constant

xomdbtodo = dbl.Xomdb('influxdb',"xomtodo")
# create logger
#module_logger = logging.getLogger('proc_compare.analysis')

class Analysis:
    def __init__(self, name):
        self.analysis_name = name
        self.analysis_version = ""
        self.variable_list = []
        self.container_list = []
        self.exclude_tags_list = []
        self.include_tags_list = []
        self.available_type_list = []
        self.runwise = False
        self.analysis_path = ""
        self.run_mode = ""
        self.command = ""
        self.result = None
        self.logger = logging.getLogger('proc_compare.analysis.'+self.analysis_name)
        self.min_run = None
        self.max_run = None

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatterch = logging.Formatter('%(name)-20s - %(levelname)-5s - %(message)s')
        ch.setFormatter(formatterch)
        # add the handlers to the logger
        self.logger.addHandler(ch)
         
    def fill_from_config(self, xomconfig):
        self.analysis_version = xomconfig.get(self.analysis_name,'analysis_version')
        containerlist = xomconfig.get(self.analysis_name,'container')
        self.container_list = containerlist.split(',')
        if xomconfig.has_option(self.analysis_name,'exclude_tags'):
            exclude_tags_list  = xomconfig.get(self.analysis_name,'exclude_tags')
            self.exclude_tags_list = exclude_tags_list.split(',')

        if xomconfig.has_option(self.analysis_name,'include_tags'):
            include_tags_list  = xomconfig.get(self.analysis_name,'include_tags')
            self.include_tags_list = include_tags_list.split(',')

        if xomconfig.has_option(self.analysis_name,'available_type'):
            available_type_list  = xomconfig.get(self.analysis_name,'available_type')
            self.available_type_list = available_type_list.split(',')

        variablelist = xomconfig.get(self.analysis_name,'variable_name')
        self.variable_list = variablelist.split(',')
        self.runwise = xomconfig.getboolean(self.analysis_name,'runwise')
        self.folder = xomconfig.get(self.analysis_name,'folder')
        self.command = xomconfig.get(self.analysis_name,'command')
        if xomconfig.has_option(self.analysis_name,'min_run'):
            self.min_run = int(xomconfig.get(self.analysis_name,'min_run'))
        if xomconfig.has_option(self.analysis_name,'max_run'):
            self.max_run = int(xomconfig.get(self.analysis_name,'max_run'))

    def print_config(self):
        print(f"##### Analysis: {self.analysis_name} version {self.analysis_version} ##########")
        print("variable list =", self.variable_list)
        print("container list =", self.container_list)
        print("exclude_tags list =", self.exclude_tags_list)
        print("include_tags list =", self.include_tags_list)
        print("runwise = ", self.runwise)
        print("command =", self.command)
        print("###################################################")

    def produce_job_filename(self):
        utc_ts =int(time.time()*1000) 
        job_filename = self.analysis_name + "_" +  str(utc_ts) + '.sh'
        return job_filename


    def write_job_file(self, job_filename, container, command):
        
        # CONTAINER_PATH="/project2/lgrandi/xenonnt/singularity-images/xenonnt-development.simg"
        # SCRIPT="/home/pellegriniq/xom_v1.py 031831"
        # USER=pellegriniq
        #SBATCH --output=/home/gaior/codes/xom/output/job_files/JobName-%j.out
        #SBATCH --error=/home/gaior/codes/xom/output/job_files/JobName-%j.err
        #RUNDIR="/home/gaior/codes/xom/backend/algorithms/scada/"
        # get the example file

        with open(constant.example_sub, 'r') as f:
            new_lines = []
            lines = f.readlines()
            for l in lines: 
                if "CONTAINER_PATH=" in l:
                    ls = l.split("=")
                    new_line = ls[0] + '=\"' + constant.container_path + container + '\"' + "\n"
                elif "SCRIPT=" in l:
                    ls = l.split("=")
                    new_line = ls[0] + '=\"'+ constant.analysis_code_folder  + self.folder  + command  + '\"' + "\n"
                elif "RUNDIR=" in l:
                    ls = l.split("=")
                    new_line = ls[0] + '=\"' + constant.analysis_code_folder + self.folder + '\"' + "\n"
                    new_line += "cd $RUNDIR"  + "\n"
                elif "SBATCH --output=" in l:
                    ls = l.split("=")
                    new_line = ls[0] + '=' + constant.job_folder + job_filename[:-3]+"-%j.out" + "\n"
                elif "SBATCH --error=" in l:
                    ls = l.split("=")
                    new_line = ls[0] + '=' + constant.job_folder + job_filename[:-3]+"-%j.err" + "\n"
                else:
                    new_line = l
                new_lines.append(new_line)

        with open(constant.job_folder + job_filename, 'w+') as f:
            for l in new_lines:
                f.write(l)


    def get_valid_runs(self, last_xom, last_daq): 
        if not self.exclude_tags_list:
            exclude_tags_query = [{}]
        else:
            exclude_tags_query = [{"tags.name":{"$ne": e}} for  e in self.exclude_tags_list]

        if not self.include_tags_list:
            include_tags_query = [{}]
        else:
            include_tags_query =  [{"tags.name": i} for i in self.include_tags_list]
        
        if not self.run_mode:
            run_mode_query = {"$ne":  " "}
        else: 
            run_mode_query = run_mode
        
        if not self.min_run:
            min_run_query = {"number":{"$gt": last_xom}}
        else:            
            min_run = max(last_xom,self.min_run)            
            print("min_run = " , min_run)
            min_run_query = {"number":{"$gt": min_run}}

        if not self.max_run:
#            max_run_query = {"$lte":last_daq}
            max_run_query = {"number": {"$lte": last_daq}}
        else: 
            max_run = min(last_daq,self.max_run)            
            print("max_run = " , max_run)
            max_run_query = {"number": {"$lte": max_run}}
 
        coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode_query,"$and" :[min_run_query, max_run_query] } ))
        valid_runs = []

        [valid_runs.append(x['number']) for x in coll]
        print (self.analysis_name, " analysis valid runs : ", valid_runs)
        return valid_runs

    def produce_list_of_runs(self,last_xom, last_daq):        
        valid_runs = self.get_valid_runs(last_xom, last_daq)
        
        if valid_runs:            
            for cont in self.container_list:
                valid_runs_str = str(valid_runs).strip('[]')
                self.logger.info('in cont %s, appending new command for runs: %s', cont, valid_runs_str)
                for r in valid_runs:
                    self.logger.info(f'producing job file for runid {r} for container {cont}')
                    command = self.command.replace('[run]',str(r))
                    job_filename = self.produce_job_filename()
                    todo_result = xomlib.Xomresult(measurement_name = "xomtodo",
                                                   analysis_name= self.analysis_name, 
                                                   analysis_version = self.analysis_version,
                                                   variable_name = "_".join(self.variable_list),
                                                   variable_value = job_filename,
                                                   runid = r,
                                                   container = cont,
                                                   tag = "todo")
                    todo_result.save()
                    self.write_job_file(job_filename, cont, command)
        else:
            self.logger.info(f"no valid run analysis {self.analysis_name}")




    def test_log(self):
        self.logger.info("just testing level INFO" )
        self.logger.debug("just testing level DEBUG" )
        self.logger.error("just testing level ERROR" )
    

# class test_scada(Analysis):
 
# class light_yield(Analysis):
#     def produce_list_of_runs(self,list_of_runs):
#         list_of_command = []
#         run_max = 50112


#         exclude_tags = self.exclude_tags_list
#         #["messy","bad", "nonsr0_configuration", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "hot_spot","abandon"]
#         exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]

#         include_tags = ["_sr1_preliminary"]
#         include_tags_query =  [{"tags.name": i} for i in include_tags]

#         run_mode ='tpc_kr83m'

#         coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode}))
#         valid_runs = []
#         [valid_runs.append(x['number']) for x in coll]
#         print ("QP analysis: ", valid_runs)
#         valid_runs.sort()
#         valid_runs = list(filter(lambda r: (r > self.min_run) & (r < run_max), valid_runs) )
#         print(valid_runs)
#         if valid_runs:            
#             self.logger.info("looping on valid runs")
#             for cont in self.container_list:
#                 valid_runs_str = str(valid_runs).strip('[]')
#                 self.logger.info('in cont %s, appending new command for runs: %s', cont, valid_runs_str)
#                 for r in valid_runs:
#                     self.logger.info(f'producing job file for runid {r} for container {cont}')
#                     command = self.command.replace('[run]',str(r).zfill(6))
#                     list_of_command.append(self.command.replace('[run]',str(r)) )
#                     job_filename = self.produce_job_filename()
#                     todo_result = xomlib.Xomresult(measurement_name = "xomtodo",
#                                                    analysis_name= self.analysis_name, 
#                                                    analysis_version = self.analysis_version,
#                                                    variable_name = "_".join(self.variable_list),
#                                                    variable_value = job_filename,
#                                                    runid = r,
#                                                    container = cont,
#                                                    tag = "todo")
#                     todo_result.save()
#                     self.write_job_file(job_filename, cont, command)
#         else:
#             self.logger.info(f"no valid run analysis {self.analysis_name}")

# class event_rate(Analysis):
#     def produce_list_of_runs(self,list_of_runs):
# #        self.min_run = 52035

#         exclude_tags = ["messy","bad", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "hot_spot","abandon"]
#         exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]

#         include_tags = ["_sr1_preliminary"]
#         include_tags_query =  [{"tags.name": i} for i in include_tags]

#         coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query}))
# #        coll = list(rundb.find({"$and" : exclude_tags_query}))
#         valid_runs = []
#         [valid_runs.append(x['number']) for x in coll]
#         print ("EVENT_RATE analysis: ", valid_runs)
#         valid_runs.sort()
#         #        valid_runs = list(filter(lambda r: r % 10 == 0, valid_runs))
#         valid_runs = list(filter(lambda r: (r > self.min_run), valid_runs) )
#         print(valid_runs)
#         if valid_runs:            
#             self.logger.info("looping on valid runs")
#             for cont in self.container_list:
#                 valid_runs_str = str(valid_runs).strip('[]')
#                 self.logger.info('in cont %s, appending new command for runs: %s', cont, valid_runs_str)
#                 for r in valid_runs:
#                     self.logger.info(f'producing job file for runid {r} for container {cont}')
#                     command = self.command.replace('[run]',str(r).zfill(6))
#                     job_filename = self.produce_job_filename()
#                     todo_result = xomlib.Xomresult(measurement_name = "xomtodo",
#                                                    analysis_name= self.analysis_name, 
#                                                    analysis_version = self.analysis_version,
#                                                    variable_name = "_".join(self.variable_list),
#                                                    variable_value = job_filename,
#                                                    runid = r,
#                                                    container = cont,
#                                                    tag = "todo")
#                     todo_result.save()
#                     self.write_job_file(job_filename, cont, command)
#         else:
#             self.logger.info(f"no valid run analysis {self.analysis_name}")

# class photo_ionization(Analysis):
#     def produce_list_of_runs(self,list_of_runs):
#         # available = ("event_basics", "peak_basics"))
#         exclude_tags = ["messy","bad", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "hot_spot","abandon"]
#         exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]

#         include_tags = ["_sr1_preliminary"]
#         include_tags_query =  [{"tags.name": i} for i in include_tags]

#         coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query}))
# #        coll = list(rundb.find({"$and" : exclude_tags_query}))
#         valid_runs = []
#         [valid_runs.append(x['number']) for x in coll]
#         print ("EVENT_RATE analysis: ", valid_runs)
#         valid_runs.sort()
#         #        valid_runs = list(filter(lambda r: r % 10 == 0, valid_runs))
#         valid_runs = list(filter(lambda r: (r > self.min_run), valid_runs) )
#         print(valid_runs)
#         if valid_runs:            
#             self.logger.info("looping on valid runs")
#             for cont in self.container_list:
#                 valid_runs_str = str(valid_runs).strip('[]')
#                 self.logger.info('in cont %s, appending new command for runs: %s', cont, valid_runs_str)
#                 for r in valid_runs:
#                     self.logger.info(f'producing job file for runid {r} for container {cont}')
#                     command = self.command.replace('[run]',str(r).zfill(6))
#                     job_filename = self.produce_job_filename()
#                     todo_result = xomlib.Xomresult(measurement_name = "xomtodo",
#                                                    analysis_name= self.analysis_name, 
#                                                    analysis_version = self.analysis_version,
#                                                    variable_name = "_".join(self.variable_list),
#                                                    variable_value = job_filename,
#                                                    runid = r,
#                                                    container = cont,
#                                                    tag = "todo")
#                     todo_result.save()
#                     self.write_job_file(job_filename, cont, command)
#         else:
#             self.logger.info(f"no valid run analysis {self.analysis_name}")







        
# class test_var_1(Analysis):
#     def produce_list_of_runs(self,list_of_runs):
#         list_of_command = []
#         run_min = 51693
#  #       valid_runs = list(filter(lambda r: r > run_min == 0, list_of_runs) )
# #        valid_runs_dict = list(rundb.find({"number" : {"$in": valid_runs}},{'number':1,'_id':0}))

# #        valid_runs_dict = list(rundb.find({"number" : {"$in": valid_runs}, "mode":"tpc_bkg"},{'number':1,'_id':0}))
# #        valid_runs = [list(valid_dict.values())[0] for valid_dict in valid_runs_dict]
# #        valid_runs = list(filter(lambda r: r % 25 == 0, valid_runs))
#         valid_runs = list(filter(lambda r: r > run_min, list_of_runs) )
#         print(valid_runs)
#         if valid_runs:            
#             self.logger.info("looping on valid runs")
#             for cont in self.container_list:
#                 valid_runs_str = str(valid_runs).strip('[]')
#                 self.logger.info('in cont %s, appending new command for runs: %s', cont, valid_runs_str)
#                 for r in valid_runs:
#                     command = self.command.replace('[run]',str(r))
#                     list_of_command.append(self.command.replace('[run]',str(r)) )
#                     utc_ts =int(time.time()) 
#                     job_filename = self.variable_name + "_" +  str(utc_ts) + '.sh'
#                     self.result = {"var_name": job_filename, "runid":r,"type":"todo","analysis_name":self.variable_name, "container": cont, "value":1,"data":None}
#                     xomdbtodo.insert(self.result)
#                     self.write_job_file(job_filename, command)
                    
# # influxdb_client.Point(constant.xomversion).tag("runid", str(result['runid'])).field(result['var_name'], result['value']).tag("type", "main")\
# #.tag("analyse", result['analysis_name']).tag("container",result['container'])
                 
#         else:
#             print("no valid run analysis ", self.variable_name)
#         return list_of_command
        

# class test_var_2(Analysis):
#     def produce_list_of_runs(self, list_of_runs):
#         list_of_command = []
#         # specific dummy conditions for test_var_2: 2 consecutive Kr runs
#         run_min = 40000
#         # find the kr83m runs within the new runs
#         coll = list(rundb.find({"number" : {"$in": list_of_runs}, "mode":"background_linked"},{'number':1}))
#         valid_runs = []
#         [valid_runs.append(x['number']) for x in coll]
#         valid_runs.sort()
#         valid_runs = list(filter(lambda r: r > run_min, valid_runs) )
#         valid_run_lists = []
#         run_size = len(valid_runs)
#         skip = False
#         for i, r in enumerate(valid_runs):                
#             if skip == True:
#                 skip = False
#                 continue
#             if i+1 < run_size:
#                 if (valid_runs[i+1] == r+1):
#                     valid_run_lists.append([valid_runs[i],valid_runs[i+1]])
#                     skip = True
#         for l in valid_run_lists[::10]: 
#             for cont in self.container_list:
#                 list_of_command.append(self.command.replace('[runs]', " ".join(map(str,l)))  + " --container " + cont)
#         if len(l) == 0:
#             logging.info("no valid run this analysis")
#         return list_of_command


# class ly_qp(Analysis):
#     def produce_list_of_runs(self, list_of_runs):
#         list_of_command = []
#         exclude_tags = ["messy","bad", "nonsr0_configuration", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "hot_spot","abandon"]
#         exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]

#         include_tags = [{"$regex":"_sr0"},"lt_24h_after_kr"]
#         include_tags_query =  [{"tags.name": i} for i in include_tags]

#         run_mode ='tpc_kr83m'
#         coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":run_mode}))
#         valid_runs = []
#         [valid_runs.append(x['number']) for x in coll]
#         print ("QP analysis: ", valid_runs)
#         valid_runs.sort()
#         valid_runs = list(filter(lambda r: r % 10 == 0, valid_runs))
#         if valid_runs:
#             for cont in self.container_list:
#                 for r in valid_runs:
#                     list_of_command.append(self.command.replace('[run]',str(r)) + " --container " + cont)
#         else:
#             print("no valid run analysis ", self.variable_name)
#         return list_of_command
        
        
        
        
        
    
