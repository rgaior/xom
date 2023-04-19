#!/usr/bin/env python
# coding: utf-8

import strax
import straxen
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sc = straxen.SCADAInterface()
parameters = {'Cathode': 'XE1T.GEN_HEINZVMON.PI',
              'PMT11': 'XE1T.CTPC.Board06.Chan011.VMon',
              'temp101': 'XE1T.CRY_TE101_TCRYOBOTT_AI.PI',
              'pt101': 'XE1T.CRY_PT101_PCHAMBER_AI.PI',
              'SLM1': 'XE1T.GEN_CE911_SLM1_HMON.PI',
              'FC104': 'XE1T.CRY_FCV104FMON.PI',
              'Anode': 'XE1T.CTPC.Board14.Chan001.VMon'
             }#parametre de l'Anode ajoute au code original

#start = 1609682275000000000
#end= 1609736527000000000
st = straxen.contexts.xenonnt()
run_id_int = 44700
run_id = str(run_id_int).zfill(6)
dfevent = st.get_df(run_id,
            targets = 'event_info',
            progress_bar=True)
start = dfevent['time'].iloc[0]
end = dfevent['endtime'].iloc[-1]
df = sc.get_scada_values(parameters, start=start, end=end, every_nth_value=1)

print(df.head())

def rmse(targets,time,units):
    mean_value=np.array(targets).mean()
    sigma=np.sqrt(((mean_value - np.array(targets)) ** 2).mean())
    plt.plot(targets,time,'o', label=str(round(mean_value, 3))+'+\-'+str(round(sigma,3)),units)
    plt.legend()
    plt.show()
    return (mean_value,sigma)


#on peut definir des unites
units=['V','charge','C','bar',' ',' ','V']
u=-1
for parameter in df.head():
    u=+1
    times=dfevent['time'].values
    rmse(df[str(parameter)],times,units[u])


t=[1,2,3,5,7,8]
tt=[1,2,3,4,5,6]


rmse(t,tt)
