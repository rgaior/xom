import subprocess
import shlex
import numpy as np
execcommand = "python output.py"
execcommand = shlex.split(execcommand)
process = subprocess.run(execcommand,
                         stdout=subprocess.PIPE,
                         universal_newlines=True)

a = process.stdout
print(a)
b = a[a.find('[')+1 : a.find(']')].strip(' ').split(' ')
new_b = [x for x in b if x != '']
print(new_b)
new_b = np.asarray(new_b,dtype=int)
print(new_b)

