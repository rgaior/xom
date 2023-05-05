#!/usr/bin/env python

import os
#import numpy as np
import time
import subprocess
import shlex
import sys
sys.path +=['../utils/']
#import locklib as ll
import utils
import constant
import dblib as dbl
import xomlib
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from argparse import ArgumentParser
import glob
import time

import logging
from logging.handlers import TimedRotatingFileHandler
logger = logging.getLogger('proc_runner')
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
import pandas as pd

def check_available(analysis_name,container,runid):
    filename = constant.availability_files_folder + analysis_name + '_' + container
    df = pd.read_csv(filename)
    if runid in df.number.values:
        return True
    else:
        return False


def sleep(delay, message=""):
    for remaining in range(delay, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("waiting " + message + ": {:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r waiting " + message + " complete!            \n")


def search_in_file(filename, to_search):
    with open(filename, "r") as f:
        a= f.read()
    if to_search in a:
        return True
    else:
        return False


def check_jobs():
#    command =  "squeue -u gaior | wc --lines"
    command =  "squeue -u gaior | wc --lines"
    execcommand = shlex.split(command)
    process = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             universal_newlines=True, shell=True)
    nr_of_lines = int(process.stdout) - 1
    print("jobs running = ", nr_of_lines)
    return nr_of_lines
    # if  nr_of_lines> job_limit:
    #     return False
    # else:
    #     return True
 
type_of_db = constant.type_of_db
xomdb = dbl.Xomdb(type_of_db,"xomdata") 
xomdbtodo = dbl.Xomdb(type_of_db,"xomtodo")
xomdbdone = dbl.Xomdb(type_of_db,"xomdone")
xomdbsubmitted = dbl.Xomdb(type_of_db,"xomsubmitted")
stop_condition = True

def main():
    print()
    print("--------------------------------------")
    print("XOM BACKEND PROCESS RUNNER module     ")
    print("--------------------------------------")
    print()
#    submitted_jobs = 0

    parser = ArgumentParser("proc_runner")
    parser.add_argument("--loglevel", type=str, help="Logging level", default='INFO')
    args = parser.parse_args()
    loglevel = args.loglevel
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(loglevel.upper())
    # create formatter and add it to the handlers
    formatterch = logging.Formatter('%(name)-20s - %(levelname)-5s - %(message)s')
    ch.setFormatter(formatterch)
    # add the handlers to the logger
    logger.addHandler(ch)
    while(stop_condition):
          
        # first check the availability. Should be replaced at some point by the query of the availability directly at the todo stage
        xomconfig = utils.get_xom_config()
    
        analysis_names = xomconfig.sections()
        analysis_list = []
        for analysis_name in analysis_names:
            containers = utils.get_from_config(xomconfig,analysis_name, 'container')
            exclude_tags = utils.get_from_config(xomconfig,analysis_name, 'exclude_tags')
            include_tags = utils.get_from_config(xomconfig,analysis_name, 'include_tags')
            available_type = utils.get_from_config(xomconfig,analysis_name, 'available_type')

            args = {}
            if exclude_tags:
                args[' --excluded '] = exclude_tags
            if include_tags:
                args[' --included '] = include_tags
            if available_type:
                args[' --available '] = available_type
            for cont in containers:
                command = "python test_data.py " + ' --container ' + cont + ' --analysis ' + analysis_name
                for key, value in zip(args.keys(), args.values()) :
                    command+= key
                    command+= " ".join(value)
                allcommand = constant.singularity_base + cont + " " + command + '\n'
                execcommand = shlex.split(allcommand)
                process = subprocess.run(execcommand,
                                         stdout=subprocess.PIPE,
                                         universal_newlines=True)
                logger.debug(process.stdout)
                logger.debug(process.stderr)

        
        sleep(constant.exec_period, 'for proc_runner execution period')
        # first loop over the submitted job and check their status:
        submitted_tables = xomdbsubmitted.query_all()
        for table in submitted_tables:
            for p in table:
                pval = p.values
                thevariable_name = pval['variable_name']
                p_analysis_name = pval['analysis_name']
                job_filename = p[thevariable_name]
                logger.debug(f"testing the status of submitted job from file {job_filename}")
                searched_name = constant.job_folder + job_filename[:-3]+"*.out"
                filenames = glob.glob(searched_name)

                if len(filenames) >1:
                    raise ValueError("two or more job files with the same name")
                if len(filenames)==1:                
                    filename = filenames[0]

                    if search_in_file(filename,"SUCCESSWITHXOM"):
                        logger.info(f"SUCCESS of JOB {job_filename}")
                        done_result = xomlib.Xomresult(measurement_name = "xomdone",
                                                       analysis_name= pval['analysis_name'],
                                                       analysis_version = pval['analysis_version'],
                                                       variable_name = pval['variable_name'],
                                                       variable_value = pval[thevariable_name],
                                                       runid = pval['runid'],
                                                       container = pval['container'],
                                                       tag = "done")
                        done_result.save()
                        xomdbsubmitted.delete_record(p)
#                        submitted_jobs -=1
                    elif search_in_file(filename,"FAILEDWITHXOM"):
                        logger.error(f"FAILED JOB {job_filename}")
                        done_result = xomlib.Xomresult(measurement_name = "xomdone",
                                                       analysis_name= pval['analysis_name'],
                                                       analysis_version = pval['analysis_version'],
                                                       variable_name = pval['variable_name'],
                                                       variable_value = pval[variable_name],
                                                       runid = pval['runid'],
                                                       container = pval['container'],
                                                       tag = "done_failed")
                        done_result.save()
                        xomdbsubmitted.delete_record(p)
#                        submitted_jobs -=1

        else:
            tables = xomdbtodo.query_all()
            for table in tables:
                for p in table:
                    submitted_jobs = check_jobs()
                    if submitted_jobs > constant.jobslimit:
#                    if submitted_jobs > constant.jobslimit:
                        logger.info(f"{submitted_jobs} jobs submitted, larger than limit (of {constant.jobslimit})")
                        break
                    pval = p.values
                    logger.debug("submitted table entry", pval)
                    thevariable_name = pval['variable_name']
                    p_analysis_name = pval['analysis_name']
                    p_container = pval['container']
                    p_runid = p['runid']
                    # check if the data are available for that runid
                    is_available = check_available(p_analysis_name,p_container,p_runid)
                    job_filename = p[thevariable_name]
                    if is_available:
                        logger.info(f'data for run {p_runid} is available, will submit the job {job_filename}')
                        execcommand = "sbatch " + constant.job_folder + job_filename
                        execcommand = shlex.split(execcommand)
                        process = subprocess.run(execcommand,
                                                 stdout=subprocess.PIPE,
                                                 universal_newlines=True)
                    
                        logger.info(f"submitted JOB {job_filename}")
                        variable_name = pval['variable_name']
                        submitted_result = xomlib.Xomresult(measurement_name = "xomsubmitted",
                                                            analysis_name= pval['analysis_name'],
                                                            analysis_version = pval['analysis_version'],
                                                            variable_name = pval['variable_name'],
                                                            variable_value = pval[variable_name],
                                                            runid = pval['runid'],
                                                            container = pval['container'],
                                                            tag = "submitted")
                        submitted_result.save()
                        xomdbtodo.delete_record(p)
                        submitted_jobs +=1
                        
                    else:
                        logger.info(f'data for {p_runid} in NOT yet available, will wait to submit the job {job_filename}')

if __name__ == "__main__":
    main()
                

