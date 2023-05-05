import strax
import straxen
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from argparse import ArgumentParser
import argparse
import cutax
from cutax.cuts.krypton_selections import KrSingleS1S2
from cutax.cuts.krypton_selections import KrDoubleS1SingleS2
import sys
sys.path +=['../../../utils/']

import xomlib


def press_run(run_id):
    
    import cutax
    st = cutax.contexts.xenonnt_offline(include_rucio_local=False,include_rucio_remote=True )
    st.register([KrSingleS1S2,KrDoubleS1SingleS2])
    st.storage += [strax.DataDirectory('/project2/lgrandi/xenonnt/processed', provide_run_metadata=True)]
    data_singleS1 = st.get_df(run_id, targets =("event_info_double", "cut_fiducial_volume", "cut_Kr_SingleS1S2"),
                   selection_str= ("cut_fiducial_volume",'cut_Kr_SingleS1S2')) 
    data_doubleS1 = st.get_df(run_id, targets =("event_info_double", "cut_fiducial_volume", "cut_Kr_DoubleS1_SingleS2"),
                   selection_str= ("cut_fiducial_volume",'cut_Kr_DoubleS1_SingleS2'))
     
    
    
    
    ES1a = 32.2
    ES1b = 9.4

    #energie du pic
    ES1 = 41.6

    
    #Light Yield

    S1_a1 = data_doubleS1['s1_a_area'].values
    S1_b1 = data_doubleS1['s1_b_area'].values
    S1_a = data_singleS1['s1_a_area'].values
    
    
    #mean
    S1amoy = np.mean(S1_a1)
    S1bmoy = np.mean(S1_b1)
    S1_41 = np.mean(S1_a)
    
    #standard deviation
    S1asigma = np.std(S1_a1)
    S1bsigma = np.std(S1_b1)
    S1_41sigma = np.std(S1_a)
    
                              
    #standard error of mean
    errorS1amoy = S1asigma/np.sqrt(len(S1_a1))
    errorS1bmoy = S1bsigma/np.sqrt(len(S1_b1))
    errorS1_41moy = S1_41sigma/np.sqrt(len(S1_a))

    #light yield 
    LYS1a = S1amoy/ES1a
    LYS1b = S1bmoy/ES1b
    LYS1_41 = S1_41/ES1                          

    #light yield error
    DLyS1a = errorS1amoy/ES1a                              
    DLyS1b = errorS1bmoy/ES1b 
    DLyS1_41 = errorS1_41moy/ES1
    
    #removing useless datas
    del data_doubleS1
    del data_singleS1
    del S1_a1
    del S1_b1
    del S1_a
    


    xomresult = xomlib.Xomresult(analysis_name="light_yield",
                                 analysis_version = "v0.0",
                                 variable_name='LYS1_41',
                                 variable_value=LYS1_41,
                                 runid=int(run_id),
                                 data= {"LYS1a":LYS1a, "DLYS1a":DLyS1a, 
                                        "LYS1b":LYS1b, "DLYS1b":DLyS1b, 
                                        "LYS1_41":LYS1_41, "DLYS1_41":DLyS1_41})
    xomresult.save()
                              
    # results = []
                              
    # results.append(run_id)
    # results.append(LYS1a)
    # results.append(DLyS1a)
    # results.append(LYS1b)
    # results.append(DLyS1b)
    # results.append(LYS1_41)
    # results.append(DLyS1_41)
    
    # np.save('/home/pellegriniq/tab22', results)

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
