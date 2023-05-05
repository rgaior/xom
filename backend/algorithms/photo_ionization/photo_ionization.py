import strax
import straxen
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from argparse import ArgumentParser
import argparse
import cutax
import utilix


import sys
sys.path +=['../../../utils/']
import xomlib



def press_run(run_id):
    
    st = cutax.contexts.xenonnt_online(include_rucio_local=False,include_rucio_remote=True )
    st.storage += [strax.DataDirectory('/project2/lgrandi/xenonnt/processed', provide_run_metadata=True)]
        
    if st.is_stored(run_id, 'event_basics') & st.is_stored(run_id, 'peak_basics'):
        
        if not st.is_stored(run_id, 'event_info'):
            try:
                # self.st.copy_to_frontend(run_id, 'peak_shadow')
                st.copy_to_frontend(run_id, 'peak_basics')
                st.copy_to_frontend(run_id, 'event_basics')
                self.st.make(run_id, 'event_info')
                print('it made event_info')
            except:
                print('Data not movable')
                return    
        
        cuts_in_use = []
     
        events = st.get_array(run_id, ['event_info', ] + cuts_in_use,
                                       selection_str=['s2_area>1000',
                                                      'z_naive>-5', 'r<70', 'z_naive<-0.5',
                                                      's1_area_fraction_top<0.65',
                                                      's1_tight_coincidence>3',
                                                      ] + cuts_in_use,
                                       keep_columns=['time', 'endtime', 's2_center_time', 's2_area'],
                                       progress_bar=False
                                       )

        peak_basics = st.get_array(run_id, ['peak_basics'],
                                            selection_str=('type' == 2),
                                            progress_bar=False,
                                            keep_columns=['time', 'endtime', 'area'],
                                            )
        
        
        if straxen.utilix_is_configured():
            c = utilix.xent_collection()
            _doc = c.find_one({'number': int(run_id)}, projection={'mode': True, 'start': True, 'tags': True, 'end': True})
            start, tag, end = _doc['start'], _doc['tags'], _doc['end']
            livetime = (end-start).total_seconds()
            #print(livetime/60)
            #livetime = (livetime / 1e9)
            #print('utilix',livetime)
        else:
            N = len(peak_basics)
            livetime = peak_basics['time'][N-1] - peak_basics['time'][0]
            #print('mine', livetime)
                                           
        min_drift_time = 300
        max_drift_time = 2200
        containers = np.zeros(len(events), dtype=[('time', np.float64), ('endtime', np.float64)])
        containers['time'] = events['s2_center_time'] + min_drift_time * 1e3
        containers['endtime'] = events['s2_center_time'] + max_drift_time * 1e3

        split_peak_basics = strax.split_by_containment(peak_basics, containers)
        result = np.concatenate(split_peak_basics)
    
        print(len(result))
        rate = len(result) / (float(livetime))       
        area = np.sum(result['area']) / np.sum(events['s2_area'])
        
        variables = []
        variables.append(rate)
        variables.append(area)
        print(f'Save sucessfully for run {run_id}',variables)
        xomresult = xomlib.Xomresult(analysis_name="photo_ionization",
                                     analysis_version = "v0.0",
                                     variable_name='area',
                                     variable_value=area,
                                     runid=int(run_id),
                                     data= {"area":area, "rate":rate})
        xomresult.xom_message(success=True)
        xomresult.save()
    else:
        print('Data not available')


    return

def main():
    print("start")

    parser = argparse.ArgumentParser()
    parser.add_argument("echo")
    args = parser.parse_args()
    print(args.echo)
    parser = ArgumentParser()
    
    press_run(args.echo)
    
    print('end')
    
if __name__ == "__main__":
    main()
