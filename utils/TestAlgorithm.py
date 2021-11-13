from utilix.config import Config
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import json

import straxen

def SaveData(result,filename):
    with open(filename,'w') as f:
        json.dump(result,f)
        f.close()


def MyAnalysis(run_id):

    print("Begin of MyAnalysis")

    """
    Here you place your analysis code
    """


    # Output

    timestamp = 123456789 # here the average run time
    LY = 1200 # a result
    sLY = 100 # its error
    chisquared = 0 # the chisquare of a possible fit

    fig = plt.figure(figsize=(9,9), dpi=100)

    results = []

    # to repeat this block for each quantity you want to monitor
    result = {}
    result['run_id'] = run_id
    result['run_ids'] = [run_id]
    result['variable_name'] = 'chargeyield'
    result['straxen_version'] = '1.2.3'
    result['strax_version'] = '1.2.3'
    result['timestamp'] = timestamp
    result['value'] = LY
    result['error'] = sLY
    result['chisquared'] = chisquared
    fig.savefig(result['variable_name']+".png")
    results.append(result)

    SaveData(results,"result.json")



def main():
    parser = ArgumentParser("MyAnalysis")

    config = Config()

    parser.add_argument("number", type=int, help="Run number to process")

    args = parser.parse_args()

    MyAnalysis(args.number)

if __name__ == "__main__":
    main()
