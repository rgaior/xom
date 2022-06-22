#!/usr/bin/env python
import os
from argparse import ArgumentParser
import pymongo
from utilix.rundb import pymongo_collection
from utilix.config import Config
import utilix
from bson.json_util import dumps
import json
from datetime import timezone, datetime, timedelta
import strax
import straxen
import sys

def load_data(filename):
    data = {}
    with open(filename,'r') as f:
        data = json.load(f)
        f.close()
    return data


def run_xom(info_file, debug):
    while(1):
        analysis_info = load_data(analysis_file)
        processing_info = load_data(processing_file)        
        for d, p in [data,processing]:
            variable_name = analysis_info.get('variable_name')
            last_run = processing_info.get('last_run')
            nr_hashes_todo = len(analysis_info.get('context'))
            if debug:
                print("analysis info:", variable_name)
            if variable_name in ['Kr83m_lightyield9kev', 'Kr83m_lightyield31kev']:
                
                
                

def main():
    parser = ArgumentParser("run_xom")

    config = Config()
    
    parser.add_argument("--analysis_file", help="variable information json file",default="./../utils/variables.json")
    parser.add_argument("--processing_file", help="processing information file",default="./../utils/processing.json")
    parser.add_argument("--debug", help="Prints extra debug information", action='store_true')

    args = parser.parse_args()
    run_xom(args.analysis_file, args.processing_file, args.debug)

if __name__ == "__main__":
    main()

