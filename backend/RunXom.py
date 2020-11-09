#!/usr/bin/env python

import os
from argparse import ArgumentParser
import pymongo
from utilix.rundb import pymongo_collection
from utilix.config import Config
import utilix
from bson.json_util import dumps
from datetime import timezone, datetime, timedelta
import strax
import straxen
import sys
from plugins.dummy import MyPlugin

def RunXom(number,to,debug):

    norecords_types  = ["pulse_counts", "pulse_counts_he", "veto_regions", "lone_hits", "peaklets","peaklets_he","merged_s2s","peak_basics","peaklet_classification","led_calibration"]                

    xom_types  = ["pulse_counts", "veto_regions", "lone_hits", "peaklets","merged_s2s","peak_basics","peaklet_classification"]                

    db = pymongo_collection('runs')

    #number = 9707

    if to>number:
        cursor = db.find({
            'number': {'$gte': number, '$lte': to}
        }).sort('number',pymongo.ASCENDING)
        print('Runs that will be processed are from {0} to {1}'.format(number,to))
    else:
        cursor = db.find({
            'number': number
        })
        print('Run that will be processed is {0}'.format(number))
    cursor = list(cursor)

    electron_lifetimes = {}

    # Runs over all listed runs
    for run in cursor:

        # Gets run number
        number = run['number']
        print('Run: {0}'.format(number))
        status = run['status']
        print('Run: {0}'.format(status))

        available_types = set()

        for data in run['data']:
            if data['location']=='UC_DALI_USERDISK' and data['status']=='transferred' and data['type'] in xom_types:
                available_types.add(data['type'])
        if len(available_types)!=len(xom_types):
            continue 
        print('All types needed available. Ready to process.')
        
        #electron_lifetimes.append(plugin[run])        
        st = straxen.contexts.xenonnt_online()
        st.register(MyPlugin)
        st.make('009679', 'fancy_peaks')
        st.get_array('009679', 'fancy_peaks')
    
    #json.append(cursor, electron_lifetimes)


def main():
    parser = ArgumentParser("RunXom")

    config = Config()

    parser.add_argument("number", type=int, help="Run number to process")
    parser.add_argument("--to", type=int, help="Process runs from the run number up to this value", default=0)
    parser.add_argument("--debug", help="Prints extra debug information", action='store_true')

    args = parser.parse_args()

    RunXom(args.number,args.to,args.debug)

if __name__ == "__main__":
    main()

