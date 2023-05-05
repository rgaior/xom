import strax
import straxen
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from argparse import ArgumentParser
import argparse
import cutax

import sys
sys.path +=['../../../utils/']

import xomlib


def cut_energy(dat, Emin, Emax):
    cut = dat[(dat <= Emax)]
    cut =  cut[(cut > Emin)]
    return cut

def press_run(run_id):
    
    st = cutax.contexts.xenonnt_online(include_rucio_local=False, include_rucio_remote=True )
    st.storage +=[strax.DataDirectory('/project2/lgrandi/xenonnt/processed', provide_run_metadata=True)]
    data = st.get_df(run_id, targets =("event_info", "cut_fiducial_volume"),
                   selection_str= ("cut_fiducial_volume"))
    Data_energy = data['e_ces']
    
    liste = [0,1,10,100,1000,10000,100000]
    Events = []
    
    e_0_100000 = len(cut_energy(Data_energy, 0, 100000))
    for i in range(len(liste)-1):
        Events.append(len(cut_energy(Data_energy, liste[i], liste[i+1])))


    xomresult = xomlib.Xomresult(analysis_name="event_rate",
                                 analysis_version = "v0.0",
                                 variable_name='e_0_100000',
                                 variable_value=e_0_100000,
                                 runid=int(run_id),
                                 data= {"e_0_100000":e_0_100000, "e_0_1":Events[0], "e_1_10":Events[1],"e_10_100":Events[2], "e_100_1000":Events[3], "e_1000_10000":Events[4], "e_10000_100000":Events[5]})
    xomresult.save()
    xomresult.xom_message(success=True)
                                  
    print(Events)

def main():
        
    parser = argparse.ArgumentParser()
    parser.add_argument("echo")
    args = parser.parse_args()
    print(args.echo)
    parser = ArgumentParser()
    print("start")

    press_run(args.echo)
    print('end')
    
if __name__ == "__main__":
    main()


 
