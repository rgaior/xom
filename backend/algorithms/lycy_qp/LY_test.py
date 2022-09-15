#libraries
from utilix.config import Config
from argparse import ArgumentParser
import json
import cutax
import strax
import straxen
import matplotlib.pyplot as plt
import numpy as np
import sys

import pandas as pd
sys.path +=['../utils/']
import xomlib as xl 
import constant as cst 


#function to save data
def SaveData(result,filename):
    with open(filename,'w') as f:
        json.dump(result,f)
        f.close()

#graph typography
font_large = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 24,
        }

#function to calculate calibration parameters (Kr83m) 

def MyAnalysis(runnumber, container):

    print("Begin of My Analysis")
    
    #access to xenonnt data
    st = cutax.contexts.xenonnt_v7()

    #charging the run
    data = st.get_df(runnumber, targets = ('event_info_double'), progress_bar=False)
    
    #timestamp 
    time = data['time'].values 
    
    #using mean to avoid edge effects
    timestamp = np.mean(time) 
    
    del time
    
    #strax version
    straxversion = strax.__version__
    
    #straxen version
    straxenversion = straxen.__version__    
    
    #for quality cuts
    def line(x,a,b):
        return a*x+b

    def diffusion_model(t,w_SE, w_t0, t_0):
        return np.sqrt(w_SE**2 + ((w_t0 - w_SE)**2 /t_0) * t)
 
    w_SE = 599.70428e-3
    w_t0 = 400.29572e-3
    t_0 = 1.0029191e-3
    
    #gamma photon energies
    ES1a = 32.2
    ES1b = 9.4
    ES1 = ES1a + ES1b
    
    #rsquare cut (for both populations)
    datacor = data[((data['s2_a_x_mlp']**2)+(data['s2_a_y_mlp']**2))<=3100]
    
    #DOUBLE S1 population 
    
    #cut large box (arbitrary)
    xmin = 100
    xmax = 700
    ymin = 30
    ymax = 250
    bigbox = datacor[(datacor['s1_a_area']<= xmax) & (datacor['s1_a_area']>= xmin) & (datacor['s1_b_area']<= ymax) & (datacor['s1_b_area']>= ymin)]

    s1_a_area = bigbox['s1_a_area'].values
    s1_b_area = bigbox['s1_b_area'].values
    
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
    datacut = datacor[(datacor['s1_a_area']<= xmax) & (datacor['s1_a_area']>= xmin) & (datacor['s1_b_area']<= ymax) & (datacor['s1_b_area']>= ymin)]

    #removing useless datas
    del bigbox, s1_a_area, s1_b_area
    
    #quality cuts
    dataline = datacut[datacut['s1_a_area_fraction_top'] < line(datacut['drift_time'],-2.3e-7,0.70)]
    dataline = dataline[dataline['s1_a_area_fraction_top'] > line(dataline['drift_time'],-2e-7,0.40)]
    
    d1 = dataline[dataline['s2_a_range_50p_area']/diffusion_model(dataline['drift_time'], w_SE, w_t0, t_0) > (-30/(dataline['drift_time']*1e-3+10)+0.8)]
    d2 = d1[d1['s2_a_range_50p_area']/diffusion_model(d1['drift_time'], w_SE, w_t0, t_0) < (30/(d1['drift_time']*1e-3+10)+1.2)]
    qualitycut = d2[(d2['drift_time']*1e-3) < 2400]
    
    #removing useless datas
    del dataline, d1, d2, datacut
    
    #standard cuts for DOUBLE S1 population
    allcutquality = qualitycut[(qualitycut['ds_s1_dt']>750) & (qualitycut['ds_s1_dt'] <2000) & (qualitycut['s1_a_n_channels'] >= 80) & (qualitycut['s1_a_n_channels'] < 225) & (qualitycut['s1_b_n_channels'] >= 25) & (qualitycut['s1_b_n_channels'] < 125)]
    
    #acceptance of DOUBLE S1 population
    acceptanceDoubleS1 = (len(allcutquality)/len(data))*100

    #calcul of parameters for Double S1 population
    
    #Light Yield

    S1_a = allcutquality['s1_a_area'].values
    S1_b = allcutquality['s1_b_area'].values

    #mean
    S1amoy = np.mean(S1_a)
    S1bmoy = np.mean(S1_b)
    
    #standard deviation
    S1asigma = np.std(S1_a)
    S1bsigma = np.std(S1_b)

    #standard error of mean
    errorS1amoy = S1asigma/np.sqrt(len(S1_a))
    errorS1bmoy = S1bsigma/np.sqrt(len(S1_b))

    #Light Yield 
    LYS1a = S1amoy/ES1a
    LYS1b = S1bmoy/ES1b

    #Light Yield error
    DLYS1a = errorS1amoy/ES1a                              
    DLYS1b = errorS1bmoy/ES1b 

    #graphe LY 32.2 keV
    fig1 = plt.figure(figsize=(12,8))
    
    ax = plt.subplot(111)

    args = dict(orientation = "horizontal", pad = 0.2, aspect = 50,
    fraction=0.046)
    
    h1 = plt.hist(S1_a, bins = 50, color = 'blue', 
          histtype = 'step', linestyle = 'solid');
    y = np.max(h1[0])
    x = np.max(h1[1])
    ax.set_title('DoubleS1 LY 32.2 keV',fontdict=font_large)
    ax.set_xlabel('S1_a [PE]',fontdict=font_large)
    ax.set_ylabel('events',fontdict=font_large)
    ax.text(6.5*(x/10),6.5*(y/8),r'LY = {:0.2f} $\pm$ {:0.2f}  $PE\cdot$$keV^{{-1}}$'.format(LYS1a,DLYS1a),color='red',fontsize='23')
    ax.text(7*(x/10),5.5*(y/8),r'acceptance= {:0.2f} %'.format(acceptanceDoubleS1) ,color='red',fontsize='23')
    
    #graphe LY 9.4 keV
    fig2 = plt.figure(figsize=(12,8))
    
    ax1 = plt.subplot(111)

    args = dict(orientation = "horizontal", pad = 0.2, aspect = 50,
    fraction=0.046)
    
    h2 = plt.hist(S1_b, bins = 50,color = 'blue', 
          histtype = 'step', linestyle = 'solid');
    y = np.max(h2[0])
    x = np.max(h2[1])
    ax1.set_title('DoubleS1 LY 9.4 keV',fontdict=font_large)
    ax1.set_xlabel('S1_b [PE]',fontdict=font_large)
    ax1.set_ylabel('events',fontdict=font_large)
    ax1.text(6.2*(x/10),6.5*(y/8),r'LY = {:0.2f} $\pm$ {:0.2f}  $PE\cdot$$keV^{{-1}}$'.format(LYS1b,DLYS1b),color='red',fontsize='23')
    ax1.text(6.8*(x/10),5.5*(y/8),r'acceptance= {:0.2f} %'.format(acceptanceDoubleS1) ,color='red',fontsize='23')
  
    #removing useless datas
    del allcutquality, qualitycut, S1_a, S1_b
    
    #results for DoubleS1 population

    #results = []
    
    # Output 1 (Light Yield 32.2 keV)
    result1 = {}
    result1['run_id'] = int(runnumber)
    
    result1['run_ids'] = [int(runnumber)]
    result1['variable_name'] = 'LYS1a'
    result1['container'] = container
    result1['timestamp'] = int(timestamp/1e9)
    result1['value'] = LYS1a
    result1['error'] = DLYS1a
    result1['chisquared'] = None
    result1['tag'] = 'test'
    outfname1 = result1['variable_name']+'_'+str(result1['run_id']) +  '_' + 'cont_' + result1['container']
    outjsonname1 = outfname1+'.json'
    outfigname1 = outfname1 + ".png"
    result1['figname'] = outfigname1
    # save the figure
    figpath1 = './algorithms/lycy_qp/tmp/' + outfigname1
    fig1.savefig(figpath1)
    
    # Output 2 (Light Yield 9.4 keV)
    
    result2 = {}
    result2['run_id'] = int(runnumber)
    
    result2['run_ids'] = [int(runnumber)]
    result2['variable_name'] = 'LYS1b'
    result2['container'] = container
    result2['timestamp'] = int(timestamp/1e9)
    result2['value'] = LYS1b
    result2['error'] = DLYS1b
    result2['chisquared'] = None
    result2['tag'] = 'test'
    outfname2 = result2['variable_name']+'_'+str(result2['run_id']) +  '_' + 'cont_' + result2['container']
    outjsonname2 = outfname2+'.json'
    outfigname2 = outfname2 + ".png"
    result2['figname'] = outfigname2
    # save the figure
    figpath2 = './algorithms/lycy_qp/tmp/' + outfigname2
    fig2.savefig(figpath2)
    
    #SINGLE S1 population
    
    #quality cuts
    
    p1 = datacor[datacor['s1_a_area_fraction_top'] < line(datacor['drift_time'],-2.3e-7,0.70)]
    print(len(p1.values))
    p2 = p1[p1['s1_a_area_fraction_top'] > line(p1['drift_time'],-2e-7,0.40)]
    p3 = p2[p2['s2_a_range_50p_area']/diffusion_model(p2['drift_time'], w_SE, w_t0, t_0) > (-30/(p2['drift_time']*1e-3+10)+0.8)]
    p4 = p3[p3['s2_a_range_50p_area']/diffusion_model(p3['drift_time'], w_SE, w_t0, t_0) < (30/(p3['drift_time']*1e-3+10)+1.2)]
    qualitycutS1 = p4[(p4['drift_time']*1e-3) < 2400]
    print(len(qualitycutS1.values))
    
    #removing useless datas
    del p1, p2, p3, p4
   
    #standard cuts
    p5 = qualitycutS1[(qualitycutS1['s1_a_n_channels'] >= 90) & (qualitycutS1['s1_a_n_channels'] < 225) & (qualitycutS1['s1_a_range_50p_area']>=60) & (qualitycutS1['s1_a_range_50p_area']<1000) & (qualitycutS1['s1_a_area_fraction_top']<0.68)]
    #(qualitycutS1['ds_s1_dt'] ==0) &
    allcutS1 = p5[(line(0.55,15,p5['s1_a_area']) > p5['s1_a_n_channels'])]
    del p5, qualitycutS1

    #SINGLES1allcut
    S1 = allcutS1['s1_a_area']
     
    #acceptance of Single S1 population
    acceptanceSingleS1 = (len(allcutS1)/len(data))*100
    
    #mean
    S1moy = np.mean(S1)
      
    #standard deviation
    S1sigma = np.std(S1)
    
    #standard error of mean
    errorS1moy = S1sigma/np.sqrt(len(S1))
    
    #Light Yield 
    LYS1 = S1moy/ES1

    #Light Yield error
    DLYS1 = errorS1moy   
    
    #graphe LY  41.6 keV
    
    fig3 = plt.figure(figsize=(12,8))
    
    ax2 = plt.subplot(111)

    args = dict(orientation = "horizontal", pad = 0.2, aspect = 50,
    fraction=0.046)
    
    h3 = plt.hist(S1, bins = 100, color = 'blue', 
          histtype = 'step', linestyle = 'solid', range = [180,720]);
    y = np.max(h3[0])
    x = np.max(h3[1])
    ax2.set_title('SingleS1 LY 41.6 keV',fontdict=font_large)
    ax2.set_xlabel('S1 [PE]',fontdict=font_large)
    ax2.set_ylabel('events',fontdict=font_large)
    ax2.text(6*(x/10),6.5*(y/8),r'LY = {:0.2f} $\pm$ {:0.2f}  $PE\cdot$$keV^{{-1}}$'.format(LYS1,DLYS1),color='red',fontsize='23')
    ax2.text(6.5*(x/10),5.5*(y/8),r'acceptance= {:0.2f} %'.format(acceptanceSingleS1) ,color='red',fontsize='23')

    # Output 3 (Light Yield 41.6 keV)
    
    result = {}
    result['run_id'] = int(runnumber)
    
    result['run_ids'] = [int(runnumber)]
    result['variable_name'] = 'LYS1'
    result['container'] = container
    result['timestamp'] = int(timestamp/1e9)
    result['value'] = LYS1
    result['error'] = DLYS1
    result['chisquared'] = None
    result['tag'] = 'test'
    result['data'] = None
    outfname = result['variable_name']+'_'+str(result['run_id']) +  '_' + 'cont_' + result['container']
    outjsonname = outfname+'.json'
    outfigname = outfname + ".png"
    result['figname'] = outfigname
    # save the figure
    figpath = './algorithms/lycy_qp/tmp/' + outfigname
    fig3.savefig(figpath)
    
    # write the json file:
    xl.SaveData(result,'./algorithms/lycy_qp/tmp/' + outjsonname)
    xl.SaveData(result1,'./algorithms/lycy_qp/tmp/' + outjsonname1)
    xl.SaveData(result2,'./algorithms/lycy_qp/tmp/' + outjsonname2)
    
    # write on the XOM data base at LNGS
    xl.UploadDataDict(result, 'dali')
    xl.UploadDataDict(result1, 'dali')
    xl.UploadDataDict(result2, 'dali')

    xl.UploadFile(figpath, 'xom@xe1t-offlinemon.lngs.infn.it:'+ cst.figfolder)
    xl.UploadFile(figpath1, 'xom@xe1t-offlinemon.lngs.infn.it:'+ cst.figfolder)
    xl.UploadFile(figpath2, 'xom@xe1t-offlinemon.lngs.infn.it:'+ cst.figfolder)


    del datacor, data, S1, allcutS1
    
    # #close all figures
    # #plt.close('all') 
    
    # #saving datas
    # SaveData(results,"result.json") 
    
    print("end of My Analysis")
    
    return 0

def main():
    parser = ArgumentParser("MyAnalysis")

    config = Config()

    parser.add_argument("number", help="Run number to process")
    parser.add_argument("--container", type=str, help="container information")

    args = parser.parse_args()

    args.number = '%06d' % int(args.number)
    
    MyAnalysis(args.number, args.container)

if __name__ == "__main__":
    main()