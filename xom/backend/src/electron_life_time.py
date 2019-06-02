import os
import sys
import warnings
import numpy as np
import time
from numpy import trapz # For integration
from pprint import pprint
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.dates as mdates          # for plotting dates
from matplotlib import gridspec            # to arrange the plots nicely
import pandas as pd
from collections import defaultdict
from scipy.stats import iqr as IQR      # for an automatic bining of the data (x or y-axis)
import scipy as sp
from iminuit import Minuit, describe, Struct
from fitter_minuit import Chi2Functor, exponential, exponential_plus_const
from configparser import ConfigParser
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle

class ElectronLifetime(object):
    
    """
    - This class is based on straxen, it needs more tuning
    - This is first attempt to use straxen data to be able to calculate electron life time using Krm
    - This a workround to select data that can give an electron life time

    """
    def __init__(self, data, plot_file_name , run_number = 1234567, source = "Kr"):
        """
	- Here the cut variable is used to clean the data to be able to have the lifetime 
	"""
        self.source = source
        self.fig_name = plot_file_name
        self.df = data
        self.file_time = time.strftime("%Y-%m-%d %H:%M:%S", \
                                       time.localtime(self.df["time"][0]/1e9))
        #self.run_number = self.df["run_number"][0]
        self.run_number = run_number
        if self.source == "Kr":   
            self.tpc_length = 96.9
            self.tpc_radius = 47.9
            self.zmin_cut = -92.9
            self.zmax_cut = -9
            self.tpc_radius_cut = 36.95
            self.cs1_min = 2.5   # this cut is in terms of log10(cs1)
            self.cs1_max = 2.65  # this cut is in terms of log10(cs1)
            self.cs2_min = 4.2   # this cut is in terms of log10(cs2)
            self.cs2_max = 4.3   # this cut is in terms of log10(cs2)
            
        elif self.source == "Rn":
            self.tpc_length = 96.9
            self.tpc_radius = 47.9
            self.zmin_cut = -92.9
            self.zmax_cut = -9
            self.tpc_radius_cut = 36.94
            self.cs1_min = 2.5   # this cut is in terms of log10(cs1)
            self.cs1_max = 2.65  # this cut is in terms of log10(cs1)
            self.cs2_min = 4.2   # this cut is in terms of log10(cs2)
            self.cs2_max = 4.3   # this cut is in terms of log10(cs2)
            
            
        
    def clean_data(self):
        """
        - Apply the cuts to the data through this function
	- There is a list variables we want to cut on, varies from source to source 
        - The list of variables for a given source can be extended 
        """
        if self.source == "Kr":
            
            list_varibales_cut = ['cs1', 'cs2', 'z','r']
            
            if set(list_varibales_cut).issubset(self.df.columns):
                
                # Eliminate NaNs 
                mask_1 = (~np.isnan(self.df[list_varibales_cut[0]]))  & (~np.isnan(self.df[list_varibales_cut[1]]))
                
                #Energy cuts (cs1 and cs2)
                mask_2  = (self.df[list_varibales_cut[0]]  < 10**self.cs1_max) &\
                          (self.df[list_varibales_cut[0]] > 10**self.cs1_min) &\
                          (self.df[list_varibales_cut[1]] < 10**self.cs2_max) &\
                          (self.df[list_varibales_cut[1]] > 10**self.cs2_min)
                
                # Position and Fiducial Volum cuts 
                mask_3 = (self.df[list_varibales_cut[3]] < self.tpc_radius_cut) &\
                         (self.df[list_varibales_cut[2]] < self.zmax_cut) &\
                         (self.df[list_varibales_cut[2]] > self.zmin_cut)

                # return the data frame with applied cuts
                return self.df[mask_1 & mask_2 & mask_3]
            
            else:
                print("Check the list of variables in your Data", list_variables_cut)
                # quit here because the list of variables you want to cut on has a problem: maybe all variables or one does not exist in the frame
                sys.exit(1)
            
        elif self.source == "Rn":
            list_varibales_cut = ['cs1', 'cs2', 'z','r']

            if set(list_varibales_cut).issubset(self.df.columns):
                # Eliminate NaNs 
                mask_1 = (~np.isnan(self.df[list_varibales_cut[0]]))  & (~np.isnan(self.df[list_varibales_cut[1]]))
                
                #Energy cuts (cs1 and cs2)
                mask_2  = (self.df[list_varibales_cut[0]]  < self.cs1_max) &\
                          (self.df[list_varibales_cut[0]] > self.cs1_min) &\
                          (self.df[list_varibales_cut[1]] < self.cs2_max) &\
                          (self.df[list_varibales_cut[1]] > self.cs2_min)
                
                # Position and Fiducial Volum cuts 
                mask_3 = (self.df[list_varibales_cut[3]] < self.tpc_radius_cut) &\
                         (self.df[list_varibales_cut[2]] < self.zmax_cut) &\
                         (self.df[list_varibales_cut[2]] > self.zmin_cut)

                # return the data frame with applied cuts
                return self.df[mask_1 & mask_2 & mask_3]
            else:
                print("Check the list of variables in your Data", list_variables_cut)
                # quit here because the list of variables you want to cut on has a problem: maybe all variables or one does not exist in the frame
                sys.exit(1)
    
    def get_bins(self, variable):
        """
        returns the x,y of a given histgram for a given variable that I name: dataframe
        """
        xInitial = variable
        
        # Here we are estimating the binwidth for the data, using
        binwidth = 2*IQR(xInitial)*(len(xInitial)**(-1/3))
        print("the value of the binwidth:", binwidth)
        if binwidth == 0:    
            print("the binwidth is 0, check this file")
            return None
        else:
            nbins = int( (xInitial.max() - xInitial.min())/binwidth )
            return nbins
        
    def get_fit_parameters(self, x,y, yerr = None, steps = [None, None] ):
        """
        this function runs Minuit and migrad to obtain the fit parameters of an exponential
        and returns a tuple of the parameters and errors: (values, errors)
        x,y: are the variables that we want to fit with Iminuit 
        """
        # Use numpy to fit the data with a plynom with order one
        # Fit the data: log(S2_bottom) vs. drift time, 
       
        fitparameters = np.polyfit(x, np.log(y), 1, full=False)

        # These are the estimate parameters that will feed to Iminuit
        
        kwdargs = dict( alpha = np.exp(fitparameters[1]), tau = 1./fitparameters[0])

        if yerr is not None:
            exponential_chi2 = Chi2Functor( exponential, x, y, yerr)
        else:
            exponential_chi2 = Chi2Functor( exponential, x, y, np.sqrt(y))
            
        if (steps[0] is None) or (steps[1] is None):
            print("If you don't give both of the steps, the fit will use 10% of the max. of the est. values")

            steps[0] = np.abs(0.1 * np.exp(fitparameters[1]))
            steps[1] = np.abs(0.1 * 1./fitparameters[0])

        iniMinuit = Minuit(exponential_chi2, error_alpha=steps[1], error_tau=steps[0], errordef=1,\
                                print_level = 0, pedantic = True, **kwdargs)
                
        iniMinuit.migrad()
        try:
            iniMinuit.hesse()
            print("The correlation between the variables is: ")
            pprint(pprint(iniMinuit.np_matrix()) )
            
        except Exception as e:
            print("Could not get the HESSE matrix")
            raise e

        iniMinuit = Minuit( exponential_chi2 , error_alpha=steps[0], error_tau=steps[1], errordef=1,\
                            print_level = 0, pedantic = False , **iniMinuit.values)

        
        iniMinuit.migrad()
        if not iniMinuit.migrad_ok():
            print("migrad was not ok: No minimization occured")
            for k in iniMinuit.values.keys():
                iniMinuit.values[k] = 0
                iniMinuit.errors[k] = 0

        else:
            iniMinuit.hesse()
            print("The fit values: ", iniMinuit.values)
            print ("The chisqr: ")
            print(iniMinuit.fval)
            
                 
        return (iniMinuit.values, iniMinuit.errors, iniMinuit.fval)


        
    def get_electron_lifetime(self):
        """
        get the electron lifetime including the plots
        """
        
        print("The number of events in the file before the cuts: ", len(self.df))
        # apply the cuts
        self.df = self.clean_data() 
        print("the number of events in the file is: ", len(self.df))

        if not len(self.df):
            print("the number of events after the cut is 0")
            return {'el_lifetime':
                {"name"   : "electron lifetime [us]",
                 "value"  : 0,
                 "error"  : 0,
                 "chi2"    : 0,
                 "ndof"    : 0,
                 "time"    : self.file_time,
                 "run_number": int(self.run_number),
                 "pvalue": 0,
                 "figure" : None }}
        # Notice here we use directly the drift time from the data frame      
        self.drift_time = self.df['drift_time']/1000
        
        # Get the number of bins in X to be able to 
        nbins = self.get_bins(self.drift_time)
        print("the number of bins:", nbins)
        if nbins:
            self.bins_dt = np.linspace(self.drift_time.min(), self.drift_time.max(), nbins)
            groups_dt = self.df.groupby(np.digitize(self.drift_time, self.bins_dt))
            
            #get the median of the energy, S2 and its error
            self.mean_dt = groups_dt["drift_time"].mean()/1000
            self.median_S2 = groups_dt["s2_bottom"].median()
            self.median_S2_err = np.array([1.253*sigmaS2/(counts**0.5) for sigmaS2,counts in \
                                           zip(groups_dt["s2_bottom"].std(),\
                                               groups_dt["s2_bottom"].count())])

            # we are going to get rid of NaNs in both S2b and drift time
            mask_nans = (~np.isnan(self.mean_dt)) & (~np.isnan(self.median_S2)) & (~np.isnan(self.median_S2_err))
            median_S2_new = self.median_S2[mask_nans]
            median_S2_err_new = self.median_S2_err[mask_nans]
            mean_dt_new =   self.mean_dt[mask_nans]

            # apply time cut: select Electron life time between 100 and 750musec only
            mask_time = (mean_dt_new > 100) & (mean_dt_new < 750)
        
            fitParameters, fitErrors,chi2 = self.get_fit_parameters(mean_dt_new[mask_time],\
                                                                    median_S2_new[mask_time],\
                                                                    median_S2_err_new[mask_time])
            ndof = len(mean_dt_new[mask_time]) -2 # we fit with A*exp(-x/Tau)
            print("The fit parameters: ", fitParameters, fitErrors, chi2/ndof)
            for k in fitParameters.keys():
                if fitParameters[k] == 0:
                    print("the fit did not converge for this data")     

                    return {'light_yield':
                            {"name"   : "electron lifetime [us]",
                             "value"  : 0,
                             "error"  : 0,
                             "chi2"    : 0,
                             "ndof"    : 0,
                             "time"    : self.file_time,
                             "run_number": int(self.run_number),
                             "pvalue"  : 0,
                             "figure" : [None]}}
            else:
                #calculate the p-value of the fit for a given ndof and a chisqr
                pvalue = 1 - sp.stats.chi2.cdf(x=chi2,  df=ndof) # Find the p-value
                print("save now the figure %s" %self.fig_name)
                self.save_figure(self.mean_dt, self.median_S2,fitParameters,fitErrors, chi2, ndof, self.median_S2_err)

                return {'el_lifetime':
                    {"name"   : "electron lifetime [us]",
                     "value"  : -1*fitParameters["tau"],
                     "error"  : fitErrors["tau"],
                     "chi2"    : chi2,
                     "ndof"    : ndof,
                     "time"    : self.file_time,
                     "run_number": int(self.run_number),
                     "pvalue" : "%.1f"% (pvalue*100), 
                     "figure" : os.path.basename(self.fig_name) }}
        else:
            warnings.warn("number of bins in drift time is 0")
            
            return {'el_lifetime':
                    {"name"   : "electron lifetime [us]",
                     "value"  : 0,
                     "error"  : 0,
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": int(self.run_number),
                     "pvalue" : 0, 
                     "figure" : None }}
            
    	#require at least 10 entries per bin for the fit
       # if (len(self.mean_dt) < 10):
       #     print("The number of entries in the mean of drifttime has < 10 entries")
       #     return {'el_lifetime':
       #             {"names"   : "electron lifetime [us]",
       #              "values"  : 0,
       #              "errors"  : 0,
       #              "chi2"    : 0,
       #              "ndof"    : 0,
       #              "time"    : self.file_time,
       #              "run_number": int(self.run_number),
       #              "pvalue"  : 0, 
       #              "figure" : None }}
    
        

    def save_figure(self, x,y,fitparameters,errfitparameters, chi2, ndof, y_err=None):
        """
        produce the figure of each run for the electron lifetime that contains ELT fit
        """
        
        # make a nice plot with the results
        matplotlib.rc('font', size=16)
        plt.rcParams['figure.figsize'] = (10.0, 8.0) # resize plots
        plt.set_cmap('autumn')
        hist, binsx, binsy = np.histogram2d(x, y,\
                                            bins=(np.linspace(x.min(), x.max(), 25),\
                                                  np.linspace(y.min(), y.max(), 25)))
        plt.pcolormesh(binsx, binsy, hist.T, norm = matplotlib.colors.LogNorm())
        
        if y_err is not None:        
            plt.errorbar(x, y, yerr = y_err, markersize=5, marker='o', color='black', linestyle='')
        else:
            plt.errorbar(x, y, yerr = np.sqrt(y), markersize=5, marker='o', color='black', linestyle='')
            
        plt.plot(x, exponential(x, **fitparameters), color='black', linewidth =2.5)
            
        plt.figtext(0.5, 0.85, r"$\tau$ =%.2f $\pm$ %.2f [$\mu$s]" %(-1*fitparameters["tau"], errfitparameters["tau"]))
            
        plt.figtext(0.5, 0.75, r"$\chi^2$ / ndof =%.2f / %i" %(chi2, ndof))

        plt.ylabel('S2 area bottom [p.e.]')
        plt.xlabel(r'Drift time [$\mu s$]')
            
        print("the figure name is: ", self.fig_name)    
        plt.savefig(self.fig_name, bbox_inches='tight')
            
        plt.close("all")
        
        return 0
