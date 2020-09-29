#!/usr/bin/env python

import os
from argparse import ArgumentParser
import pymongo
from utilix.rundb import pymongo_collection
from utilix.config import Config
import utilix
from bson.json_util import dumps
from datetime import timezone, datetime, timedelta



def RunXom(number,to,debug):

    db = pymongo_collection('runs')

#    number = 9269

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

    # Runs over all listed runs
    for run in cursor:

        # Gets run number
        number = run['number']
        print('Run: {0}'.format(number))
        status = run['status']
        print('Run: {0}'.format(status))




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

