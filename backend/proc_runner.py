#!/usr/bin/env python

import os
import numpy as np
import time
import subprocess
import shlex
import sys
sys.path +=['../utils/']
import locklib as ll

command_file = 'list_of_commands.txt'

while(1):
    time.sleep(1)
#    ll.release(fd)
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
            execcommand = shlex.split(execcommand)
            process = subprocess.run(execcommand,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
            print(process)        
            with open(command_file, "w") as f:
                for line in lines[1:]:
                        f.write(line)
            ll.release(fd)