import straxen
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from argparse import ArgumentParser
import argparse
import sys

sys.path +=['../../../utils/']

import xomlib


def press_run(runid):
    print(runid)
    sc = straxen.SCADAInterface() 
    parameters = {'Pcryo':'XE1T.CRY_PT101_PCHAMBER_AI.PI'}
    st = straxen.contexts.xenonnt_online()
    sc.context = st
    run_number = str(runid)
    dfbg = sc.get_scada_values(parameters, run_id= run_number, every_nth_value=1)     
    data = dfbg.to_numpy()
    mean = np.mean(data)
    
    xomresult = xomlib.Xomresult(analysis_name="test_scada",
                                 analysis_version = "v0.0",
                                 variable_name='XE1T.CRY_PT101_PCHAMBER_AI.PI',
                                 variable_value=mean,
                                 runid=runid,
                                 runids=["012", "013"])
    xomresult.save()

    # if(xom_saver("test_scada",'XE1T.CRY_PT101_PCHAMBER_AI.PI',runid,mean, datatype="main")):
    #     xom_message(sucess=True)
    # else:
    #     xom_message(sucess=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runid",type=int,help='runid')
    args = parser.parse_args()
    print(args.runid)
    parser = ArgumentParser()

    press_run(args.runid)
    
if __name__ == "__main__":
    main()

