#!/usr/bin/env python

import os
#import numpy as np
import time
import subprocess
import shlex
import sys
sys.path +=['../utils/']
#import locklib as ll
import constant
import dblib as dbl
import xomlib
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

command_file = 'list_of_commands.txt'
import logging
from logging.handlers import TimedRotatingFileHandler
logger = logging.getLogger('proc_compare')
log_format = "%(asctime)s  - %(name)s - %(levelname)s - %(message)s"
log_level = 10
handler = TimedRotatingFileHandler('../logs/proc_runner.log', when="midnight", interval=1)
logger.setLevel(log_level)
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
# add a suffix which you want
handler.suffix = "%Y%m%d"
# finally add handler to logger    
logger.addHandler(handler)
 
type_of_db = constant.type_of_db
xomdb = dbl.Xomdb(type_of_db,"xomdata") 
xomdbtodo = dbl.Xomdb(type_of_db,"xomtodo")
xomdbdone = dbl.Xomdb(type_of_db,"xomdone")
stop_condition = True
while(stop_condition):
    tables = xomdbtodo.query_all()
    for table in tables:
        print (table)
        for p in table:
            pval = p.values
            print(pval)
            thevariable_name = pval['variable_name']
            p_analysis_name = pval['analysis_name']
#            pdict = xomdbtodo.get_dict_from_record(p)            
            job_filename = p[thevariable_name]
            execcommand = "sbatch " + constant.job_folder + job_filename
            execcommand = shlex.split(execcommand)
            process = subprocess.run(execcommand,
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)

            variable_name = pval['variable_name']
            done_result = xomlib.Xomresult(measurement_name = "xomdone",
                                           analysis_name= pval['analysis_name'],
                                           analysis_version = pval['analysis_version'],
                                           variable_name = pval['variable_name'],
                                           variable_value = pval[variable_name],
                                           runid = pval['runid'],
                                           container = pval['container'],
                                           tag = "done")
            done_result.save()
#            xomdbdone.insert(pdict)
#            write_api_done = xomdbdone.client.write_api(write_options=SYNCHRONOUS)
#            write_api_done.write(bucket="xom", org="xenon", record=p)
    stop_condition = False
                

    

#     #    ll.release(fd)
#     time.sleep(60)
#     fd = ll.acquire(command_file,5)
#     with open(command_file, "r") as f:
#         lines = f.readlines()
#         if  os.path.getsize(command_file) == 0:
#             print('empy file')
#             print('no line to proceed anymore')
#             ll.release(fd)
#             continue
#         else:
#             print('length of lines = ', len(lines))
#             execcommand = lines[0]
#             print('line to process on  proc runner = ', execcommand )
#             logger.info(execcommand)
#             execcommand = shlex.split(execcommand)
#             process = subprocess.run(execcommand,
#                                     stdout=subprocess.PIPE,
#                                     universal_newlines=True)
#             logger.info(process)        
#             with open(command_file, "w") as f:
#                 for line in lines[1:]:
#                         f.write(line)
#             ll.release(fd)
# #    time.sleep(constant.exec_period)
    
