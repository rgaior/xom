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
import pprint 

#from ..utils.locklib  import acquire
sys.path +=['../utils/']
import locklib as ll

ll.acquire('list_of_commands.txt',3)
db = pymongo_collection('runs')

print(len(db.distinct('number')))
#pprint.pprint(db.find_one({'number':38657})['data'][0]['meta']['straxen_version'])
