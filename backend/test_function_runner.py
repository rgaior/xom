#!/usr/bin/env python
import os
from argparse import ArgumentParser
from socket import timeout
import json
from datetime import timezone, datetime, timedelta
import sys
import pprint 
import numpy as np
import time
import configparser
import shlex
import subprocess
sys.path +=['../utils/']
import constant




def check_jobs(job_limit):
#    command =  "squeue -u gaior | wc --lines"
    command =  "squeue -u gaior | wc --lines"
    execcommand = shlex.split(command)
    process = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             universal_newlines=True, shell=True)
    nr_of_lines = process.stdout
    print(int(nr_of_lines) -1)
    # if  nr_of_lines> job_limit:
    #     return False
    # else:
    #     return True


def main():
    print()
    print("--------------------------------------")
    print("TEST FUNCTION for BACKEND    ")
    print("--------------------------------------")
    print()

    parser = ArgumentParser("test_function")
    parser.add_argument("--jobs", help="test the xomdb functions", action='store_true')
    args = parser.parse_args()

        
    if args.jobs:
        check_jobs(3)



    # a = 0

    # prev_last_run_xom = 0
    # prev_last_run_daq = 0 
    # try:
    #     last_run_xom = int(dbl.get_max("run_id",xomdatadb))
    # except(IndexError):
    #     last_run_xom = 0    
    #     print("latest entry in XOM DB = ",last_run_xom)  

    # ##############################################
    # ### filling a list with analysis instances ###
    # ##############################################
    # analysis_list = []
    # for analysis_name in analysis_names:
    #     an = getattr(analysismodule, analysis_name )(analysis_name)
    #     an.fill_from_config(xomconfig)
    #     analysis_list.append(an)
    # if verbose:
    #     for an in analysis_list:
    #         an.printname()

    # ##############################
    # ### Starting the main loop ###
    # ##############################
    # while(a<1):
    #     # check for new runs in run DB
    #     last_run_daq = dbl.get_max("number", rundb)
        
    #     if prev_last_run_daq==last_run_daq:
    #         logger.info('no new run')
    #         print("no new run")
    #         continue
    #     if last_run_daq > prev_last_run_daq:
    #         prev_last_run_daq  = last_run_daq
        
    #     # check if xom is up to date
    #     for an in analysis_list:
    #         try: 
    #             last_run_xom = dbl.get_max("run_id",xomdatadb,query={"var_name": an.variable_name})
    #         except(IndexError):
    #             if verbose:
    #                 print("new variable here")
    #             logger.info("new variable in xom")
    #             last_run_xom = 0
    #         # 
    #         try:
    #             if last_run_daq < last_run_xom:
    #                 raise ValueError
    #             elif last_run_daq == last_run_xom:
    #                 logger.info("nothing to do, analysis %s up to date", an.variable_name)
    #                 continue
    #             else:
    #                 list_of_new_runs = list(range(last_run_xom +1, last_run_daq +1 ,1))
    #         except(ValueError):
    #             logger.error('xom run larger than last rundb run, exiting')
    #             print(f"last run of XOM ( = {last_run_xom}) is larger than last run of DAQ ( = {last_run_daq})...")
    #             print("Check xom data base, something is really wrong, will exit now")

    #         #produce list of runs according the analysis:
    #         list_of_command = an.produce_list_of_runs(list_of_new_runs)

    #         # # write the command list in the text file
    #         # for command in list_of_command:
    #         #     container = command.split()[-1]
    #         #     total_command = constant.singularity_base + container + " " + command + '\n'
    #         #     #insure the file is not locked by other process:
    #         #     fd = ll.acquire(command_file, timeout=10)
    #         #     with open(command_file, 'a+') as f:
    #         #         f.write(total_command)
                
    #         #     # unlock the txt file 
    #         #     ll.release(fd)

    #     time.sleep(constant.exec_period)
    

        



if __name__ == "__main__":
    main()







 




# #    a = 1
# # pprint.pprint(f'last run {last_run_daq}')
# # pprint.pprint(f'last run xom {last_run_xom}')
# # #print("xom data = ", xomdata.find_one())
#     # coll = list(rundb.find({"number" : {"$in": [39321, 39323]}, "mode":"tpc_kr83m"},{'number':1}))
#     # for x in coll:
#     #     print(x)
        

# #def last_run_check():



