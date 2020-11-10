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
    depends_on = ('peak_basics')

    def infer_dtype(self):
        print("infer")
        dtype = strax.time_fields + [(('Electron life time in TPC', 'elif'), np.float32)]
        return dtype
    
    def compute(self, peaks, start, end):
        print("Computing...")
        res = np.ones(1, dtype=strax.time_fields + [(('Electron life time in TPC', 'elif'), np.float32)])
        res['time'] = start
        res['endtime'] = end
        option_value = self.config['peak_split_min_area']
        res['elif'] = compute_elife(peaks, option_value)
        return res
    
def compute_elife(peak_basics, option_value):
    print("elife")
    return 100
    
