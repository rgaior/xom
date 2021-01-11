import numpy as np
import matplotlib.pyplot as plt
#pd.options.display.max_colwidth = 100                                                                                                            
import straxen
st = straxen.contexts.xenonnt_online()

run_id = '011657'

@straxen.mini_analysis(requires=('event_basics',))
def plot_peak_classification(events):

#    plt.scatter(events['s1_area'], events['s2_area'],                                                                                            
#                s=s, marker='.', edgecolors='none')                                                                                              
    print("Events:",len(events['s1_area']),events['s1_area'])

st.plot_peak_classification(run_id)
