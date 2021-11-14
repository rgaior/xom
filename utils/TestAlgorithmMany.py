#from utilix.config import Config
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
import json
import random
#import straxen

# dummy range number up to 3000
runrange = range(0,3000)
# light yield range [mean, sigma]:
lyrange = {'mean':15,'sigma':5}
# charge yield range [mean, sigma]:
cyrange = {'mean':10,'sigma':5}
# electron lifetime [mean, sigma]:
eltrange = {'mean':100,'sigma':5}

#straxen version range:
straxenrange = ['1.2.1','1.2.2','1.2.3']
straxrange = ['2.2.1','2.2.2','2.2.3']

def SaveData(result,filename,mode='w'):
    with open(filename,mode) as f:
        json.dump(result,f)
        f.close()




def MyAnalysis(analysis, numberofrun,mode='a'):

    print("Begin of MyAnalysis")

    """
    Here you place your analysis code
    """
    runs = runrange[:numberofrun]
    results = []
    for run in runs:
    # Output

        # dummy start from 1/1/2020 each run is 1 one and they are consecutive
        timestamp = 1577833200 + run*3600
        if analysis == 'lightyield':
            LY = np.random.normal(lyrange['mean'], lyrange['sigma'], 1)[0] # a result
            sLY = 0.1*LY # its error
            chisquared = 0 # the chisquare of a possible fit

            # to repeat this block for each quantity you want to monitor
            result = {}
            run_id = run
            result['run_id'] = run_id
            result['run_ids'] = [run_id]
            result['variable_name'] = 'lightyield'
            result['straxen_version'] = random.choice(straxenrange)
            result['strax_version'] = random.choice(straxrange)
            result['timestamp'] = timestamp
            result['value'] = LY
            result['error'] = sLY
            result['chisquared'] = chisquared
            result['tag'] = 'test'
            data = np.random.normal(LY, sLY, 1000)
            fig = plt.figure(figsize=(9,9), dpi=100)
            plt.hist(data)
            figname = result['variable_name']+'_'+str(result['run_id']) +  '_' + 'strax' + result['strax_version'] + '_' + 'straxen' + result['straxen_version']+".png"
            fig.savefig(figname)
            result['figname'] = figname
            print(result)
            results.append(result)

        if analysis == 'chargeyield':
            CY = np.random.normal(cyrange['mean'], cyrange['sigma'], 1) # a result
            sCY = 0.1*CY # its error
            chisquared = 0 # the chisquare of a possible fit
            results = []

            # to repeat this block for each quantity you want to monitor
            result = {}
            result['run_id'] = run_id
            result['run_ids'] = [run_id]
            result['variable_name'] = 'chargeyield'
            result['straxen_version'] = random.choice(straxen)
            result['strax_version'] = random.choice(strax)
            result['timestamp'] = timestamp
            result['value'] = CY
            result['error'] = sCY
            result['chisquared'] = chisquared
            result['tag'] = 'test'
            results.append(result)
    print(results)
    SaveData(results,"result.json",mode)



def main():
    parser = ArgumentParser("MyAnalysis")

#    config = Config()

    parser.add_argument("numberofrun", type=int, help="number of runs to process")
    parser.add_argument("analysis", type=str, choices=['lightyield', 'chargeyield'], help="name of variable to be process")
    parser.add_argument("--overwrite",  help="name of variable to be process",action='store_true')
 
    args = parser.parse_args()
    numberofrun = args.numberofrun
    analysis = args.analysis
    overwrite = args.overwrite
    if numberofrun > 3000:
        raise Exception('x should not exceed 3000. The value of x was: {}'.format(numberofrun))
    if overwrite:
        MyAnalysis(analysis, args.numberofrun,'w')
    else:
        MyAnalysis(analysis, args.numberofrun,'a')
        
if __name__ == "__main__":
    main()
