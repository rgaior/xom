#!/usr/bin/env python

import os
import numpy as np
import time
import subprocess
import shlex
import sys
sys.path +=['../utils/']
import locklib as ll
import constant as constant

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

while(1):
#    ll.release(fd)
    time.sleep(60)
    fd = ll.acquire(command_file,5)
    with open(command_file, "r") as f:
        lines = f.readlines()
        if  os.path.getsize(command_file) == 0:
            print('empy file')
            print('no line to proceed anymore')
            ll.release(fd)
            continue
        else:
            print('length of lines = ', len(lines))
            execcommand = lines[0]
            print('line to process on  proc runner = ', execcommand )
            logger.info(execcommand)
            execcommand = shlex.split(execcommand)
            process = subprocess.run(execcommand,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
            logger.info(process)        
            with open(command_file, "w") as f:
                for line in lines[1:]:
                        f.write(line)
            ll.release(fd)
#    time.sleep(constant.exec_period)
    