#function

#libraries
from utilix.config import Config
from argparse import ArgumentParser
import json

import straxen
import time as timer
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import scipy as sp
from scipy import optimize
from scipy.optimize import curve_fit
import pandas as pd
from matplotlib import patches
from multihist import Histdd

def SaveData(result,filename):
    with open(filename,'w') as f:
        json.dump(result,f)
        f.close()
    

def MyAnalysis(run_id):

    print("Begin of My Analysis")

    #import straxen
    st = straxen.contexts.xenonnt_online()

    #charging the run
    data1=st.get_df(run_id, targets = ('event_info_double'), progress_bar=False)
    
    #timestamp
    time=data1['time'].values 
    timestamp=np.mean(time)
    del time
    
     #for quality cuts
    def line(x,a,b):
        return a*x+b

    def diffusion_model(t,w_SE, w_t0, t_0):
        return np.sqrt(w_SE**2 + ((w_t0 - w_SE)**2 /t_0) * t)
 
    w_SE= 599.70428e-3
    w_t0= 400.29572e-3
    t_0= 1.0029191e-3
    
    #valeurs des pics
    ES1a=32.2
    ES1b=9.4

    #energie du pic
    ES1=41.6

    
    #Double S1 population 
    
    #cut large box(arbitrary)
    xmin=100
    xmax=700
    ymin=30
    ymax=250
    grosseboite=data1[(data1['s1_a_area']<= xmax) & (data1['s1_a_area']>= xmin) & (data1['s1_b_area']<= ymax) & (data1['s1_b_area']>= ymin)]

    s1_a_area = grosseboite['s1_a_area'].values
    s1_b_area = grosseboite['s1_b_area'].values
    
    #litlle box (automatic)
    
    #mean
    xmoy=np.mean(s1_a_area)
    ymoy=np.mean(s1_b_area)
    
    #standard deviation
    sigmax=np.std(s1_a_area)
    sigmay=np.std(s1_b_area)

    sigma=2.5 #arbitrary but works well

    #new definiton of the box
    xmin=xmoy-sigma*sigmax
    xmax=xmoy+sigma*sigmax
    ymin=ymoy-sigma*sigmay
    ymax=ymoy+sigma*sigmay
    
    #cut box
    databoite=data1[(data1['s1_a_area']<= xmax) & (data1['s1_a_area']>= xmin) & (data1['s1_b_area']<= ymax) & (data1['s1_b_area']>= ymin)]

    #cut rsquare
    datacut=data1[((databoite['s2_a_x_mlp']**2)+(data1['s2_a_y_mlp']**2))<=3100]
    
    #removing useless datas
    del databoite
    del grosseboite
    del s1_a_area
    del s1_b_area
    
    #quality cut
    dataline = datacut[datacut['s1_a_area_fraction_top'] < line(datacut['drift_time'],-2.3e-7,0.70)]
    dataline = dataline[dataline['s1_a_area_fraction_top'] > line(dataline['drift_time'],-2e-7,0.40)]
    
    d1=dataline[dataline['s2_a_range_50p_area']/diffusion_model(dataline['drift_time'], w_SE, w_t0, t_0) > (-30/(dataline['drift_time']*1e-3+10)+0.8)]
    d2 = d1[d1['s2_a_range_50p_area']/diffusion_model(d1['drift_time'], w_SE, w_t0, t_0) < (30/(d1['drift_time']*1e-3+10)+1.2)]
    qualitycut=d2[(d2['drift_time']*1e-3) < 2400]
    
    #removing useless datas
    del dataline
    del d1
    del d2
    
    #maxime cut for Double S1 population
    allcutquality=qualitycut[(qualitycut['ds_s1_dt']>750) & (qualitycut['ds_s1_dt'] <2000) & (qualitycut['s1_a_n_channels'] >= 80) & (qualitycut['s1_a_n_channels'] < 225) & (qualitycut['s1_b_n_channels'] >= 25) & (qualitycut['s1_b_n_channels'] < 125)]
    
    #acceptance of Double S1 population
    acceptanceDoubleS1=(len(allcutquality)/len(data1))*100

    #calcul of parameters for Double S1 population
    
    #Light Yield

    S1_a1=allcutquality['s1_a_area'].values
    S1_b1=allcutquality['s1_b_area'].values

    #mean
    S1amoy=np.mean(S1_a1)
    S1bmoy=np.mean(S1_b1)
    
    #standard deviation
    S1asigma=np.std(S1_a1)
    S1bsigma=np.std(S1_b1)

    #standard error of mean
    errorS1amoy=S1asigma/np.sqrt(len(S1_a1))
    errorS1bmoy=S1bsigma/np.sqrt(len(S1_b1))

    #light yield 
    LYS1a=S1amoy/ES1a
    LYS1b=S1bmoy/ES1b

    #light yield error
    DLyS1a=errorS1amoy/ES1a                              
    DLyS1b= errorS1bmoy/ES1b 
    #graphe
    
    fig1=plt.figure(figsize=(12,8))
    
    ax = plt.subplot(111)

    args = dict(orientation = "horizontal", pad = 0.2, aspect = 50,
    fraction=0.046)
    
    plt.hist(S1_a1, bins = 150, color = 'red', 
          histtype = 'step', linestyle = 'solid', range = [200,500],label='');
                                           
    #plt.text(80,530,r'LY_S1_a = {:0.3f} $\pm$ {:0.3f}  '.format(Lys1a1,DLys1a1),color='red',fontsize='20')
    #plt.text(80,510,r'LY_S1_b = {:0.3f} $\pm$ {:0.3f}  '.format(Lys1b1,DLys1b1) ,color='red',fontsize='20')
    #plt.text(80,490,r'acceptance= {:0.3f} %'.format(acceptanceDoubleS1) ,color='red',fontsize='20')
    #plt.savefig("Double S1 population.jpg")
    ax.legend(fontsize=17)
    
    
    fig2=plt.figure(figsize=(12,8))
    
    ax = plt.subplot(111)

    args = dict(orientation = "horizontal", pad = 0.2, aspect = 50,
    fraction=0.046)
    
    plt.hist(S1_b1, bins = 150, color = 'red', 
          histtype = 'step', linestyle = 'solid', range = [0,300],label='');
                                           
    #plt.text(80,530,r'LY_S1_a = {:0.3f} $\pm$ {:0.3f}  '.format(Lys1a1,DLys1a1),color='red',fontsize='20')
    #plt.text(80,510,r'LY_S1_b = {:0.3f} $\pm$ {:0.3f}  '.format(Lys1b1,DLys1b1) ,color='red',fontsize='20')
    #plt.text(80,490,r'acceptance= {:0.3f} %'.format(acceptanceDoubleS1) ,color='red',fontsize='20')
    #plt.savefig("Double S1 population.jpg")
    ax.legend(fontsize=17)
    
    
    #removing useless datas
    del datacut
    del allcutquality
    del qualitycut
    del S1_a1
    del S1_b1

    results = []
    
    # Output 1 (Light Yield S1a)
    
    result = {}
    result['run_id'] = run_id
    result['run_ids'] = [run_id]
    result['variable_name'] = 'lightyeld_S1a'
    result['straxen_version'] = '1.2.3'
    result['strax_version'] = '1.2.3'
    result['name'] = 'Light Yield S1a'
    result['unit'] = '[PE/keV]'
    result['timestamp'] = timestamp
    result['value'] = LYS1a
    result['error'] = DLyS1a
    result['chisquared'] = 0
    fig1.savefig('lightyeld_S1a.png')
    results.append(result)   
    
    # Output 2 (Light Yield S1b)
    
    result = {}
    
    result['run_id'] = run_id
    result['run_ids'] = [run_id]
    result['variable_name'] = 'lightyeld_S1b'
    result['straxen_version'] = '1.2.3'
    result['strax_version'] = '1.2.3'
    result['name'] = 'Light Yield S1b'
    result['unit'] = '[PE/keV]'
    result['timestamp'] = timestamp
    result['value'] = LYS1b
    result['error'] = DLyS1b
    result['chisquared'] = 0
    fig2.savefig('lightyeld_S1b.png')
    results.append(result)
    
    #close all figures
    plt.close('all') 
    
    #saving datas
    SaveData(results,"result.json") 
    
    print("end of My Analysis")
    
    return


def main():
    parser = ArgumentParser("MyAnalysis")

    config = Config()

    parser.add_argument("number", help="Run number to process")

    args = parser.parse_args()

    args.number = '%06d' % int(args.number)

    MyAnalysis(args.number)

if __name__ == "__main__":
    main()
