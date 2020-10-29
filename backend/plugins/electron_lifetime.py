import strax
import straxen
import numpy as np
from scipy.optimize import curve_fit
st = straxen.contexts.xenon1t_dali()


class electron_lifetime(strax.Plugin) :

    # Name of the data type this plugin provides
    provides = 'electron_lifetime'

    # Data types this plugin requires
    depends_on = ('run_id', 'optionals parameters')

    # Numpy datatype of the output
    #dtype = straxen.electron_lifetime.dtype

    # Version of the plugin. Increment this if you change the algorithm.
    __version__ = '0.7.0'


    def compute(self, run_id, minS2=1e3, maxS2=5e4, min_drft=1e5, max_drft=7e5, binsx=100, binsy=100, bxby=True):
        #runs selections
        df = st.get_df(run_id, 'event_info')

        #cuts, those cuts can be modified on arguments
        S2 = df.s2_area[(df.s2_area> minS2) & (df.s2_area< maxS2)]
        DelT = df.drift_time[(df.s2_area> minS2) & (df.s2_area< maxS2)]
        DelTc = DelT[(DelT> min_drft) & (DelT<max_drft)]
        S2c = S2[(DelT> min_drft) & (DelT<max_drft)]

        bins = [binsx,binsy]
        #due to some error of fitting binx must be >= biny
        if binsx>binsy and bxby == True :
            binsx=binsy
            import warnings
            warnings.warn("To fit correctly, now binx=biny, to display the original error message put bxby=False")

        #extracting histogram data
        H,xedges,yedges = np.histogram2d(DelTc,S2c,bins,normed=False)
        bin_centers_x = (xedges[:-1]+xedges[1:])/2.0
        bin_centers_y = (yedges[:-1]+yedges[1:])/2.0

        #fitting a gaussians on y with a loop on x
        def gaussian(x, amp, mu, sig):
            return amp * np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

        dtf = bin_centers_x
        S2f = np.ones(binsx)
        S2fr = np.ones(binsx)
        for i in range(binsx):
            maxH = np.amax(H[i])
            ind_max = np.argsort(H[i])
            popt, pcov = curve_fit(gaussian, bin_centers_y, H[i], p0=[maxH,bin_centers_y[ind_max[-1]],np.amax(bin_centers_y)/10])
            if 1 in popt or np.inf in pcov : raise ValueError('The fitting is wrong, please check input data or manually change arguments')
            x2 = bin_centers_y[(bin_centers_y>popt[1]-2*popt[2]) & (bin_centers_y<popt[1]+2*popt[2])]
            y2 = H[i][(bin_centers_y>popt[1]-2*popt[2]) & (bin_centers_y<popt[1]+2*popt[2])]
            popt, pcov = curve_fit(gaussian, x2, y2, p0=[maxH,bin_centers_y[ind_max[-1]],np.amax(bin_centers_y)/10])
            if 1 in popt or np.inf in pcov : raise ValueError('The fitting is wrong, please check input data or manually change arguments')
            S2f[i] = popt[1]
            S2fr[i] = popt[2]

        #fitting the 2d histogram pattern
        def func(x, A, tau):
            C = A * np.exp(-x/tau)
            return C

        popt2, pcov2 = curve_fit(func, dtf, S2f, p0=[np.amax(S2f),2e5])
        if 1 in popt2 or np.inf in pcov2 : raise ValueError('The fitting is wrong, please check input data or manually change arguments')

        e_life_t = popt2[1]
        char_yd = popt2[0]
        mx_cov = pcov2
        e_lifetime = {'e_life_t':popt2[1],'char_yd':popt2[0],'mx_cov':pcov2}

        return e_lifetime
