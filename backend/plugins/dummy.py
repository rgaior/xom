import strax
import straxen
import numpy as np

@strax.takes_config(
strax.Option('peak_split_min_area', default=40.,
             help='Minimum area to evaluate natural breaks criterion. '
                  'Smaller peaks are not split.'))

class MyPlugin(strax.Plugin):
    """
    """
    provides = ('fancy_peaks')

    data_kind = 'fancy_peaks'
<<<<<<< HEAD
    #depends_on = 'peak_basics'
    depends_on = 'peaklets'
    
=======
    depends_on = ('peak_basics')

>>>>>>> e7d61d47667e4a6bd35c8a2fed07d7eec2704367
    def infer_dtype(self):
        print("infer")
        dtype = strax.time_fields + [(('Electron life time in TPC', 'elif'), np.float32)]
        
        return dtype
    
<<<<<<< HEAD
    def compute(self, peaklets, start, end):
=======
    def compute(self, peaks, start, end):
        print("Computing...")
>>>>>>> e7d61d47667e4a6bd35c8a2fed07d7eec2704367
        res = np.ones(1, dtype=strax.time_fields + [(('Electron life time in TPC', 'elif'), np.float32)])
        res['time'] = start
        res['endtime'] = end
        option_value = self.config['peak_split_min_area']
<<<<<<< HEAD
        res['elif'] = compute_elife(peaklets, option_value)
        print("doing stuff")
        
        return res
    
def compute_elife(peaklets, option_value):
=======
        res['elif'] = compute_elife(peaks, option_value)
        return res
    
def compute_elife(peak_basics, option_value):
    print("elife")
>>>>>>> e7d61d47667e4a6bd35c8a2fed07d7eec2704367
    return 100
    
