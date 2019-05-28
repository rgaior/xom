import os
import sys
import warnings
import numpy as np
import time
from numpy import trapz # For integration
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.dates as mdates          # for plotting dates
from matplotlib import gridspec            # to arrange the plots nicely
import pandas as pd
from collections import defaultdict
from scipy.stats import iqr as IQR

from iminuit import Minuit, describe, Struct
from fitter_minuit import Chi2Functor, exponential, exponential_plus_const
from configparser import ConfigParser
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle

class ElectronLifetime(object):
    
    """
    - This class is based on straxen, it needs more tuning
    - This is first attempt to use straxen data to be able to calculate electron life time using KR
    - This a workround to select data that can give an electron life time

    """
    def __init__(self, data, plot_file_name , correction = True, source = "kr"):
        """
	- Here the cut variable is used to clean the data to be able to have the lifetime 
	"""
        self.file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.df["event_time"][0]/1e9))
        self.run_number = data["run_number"][0]
        self.source = source
        self.fig_name = plot_file_name
        self.df = data 
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
	- There is a list variables we want to cut on, varies from source to source and also can can be extended 
        """
        if self.source == "Kr":
            
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
                {"names"   : ["electron lifetime [us]"],
                 "values"  : [-1],
                 "errors"  : [0],
                 "chi2"    : 0,
                 "ndof"    : 0,
                 "time"    : self.file_time,
                 "run_number": int(self.run_number),
                 "figures" : [None] }}
        # Notice here we use directly the drift time from the data frame      
        self.drift_time = self.df['drift_time']/1000
        self.max_time_drift = self.drift_time.max()
        self.min_time_drift = self.drift_time.min()
        
        # Here also we use directly the s2_bottom, we can't differentiate between the different gamma peaks from Kr for example 
        self.max_s2 = self.df['s2_bottom'].max()
        self.min_s2 = self.df['s2_bottom'].min()
        
        # Get the number of bins in X to be able to 
        nbins = self.get_bins(self.drift_time)
        print("the number of bins:", nbins)
        if nbins:
            self.bins_dt = np.linspace(self.min_time_drift, self.max_time_drift, nbins)
            groups_dt = self.df.groupby(np.digitize(self.drift_time, self.bins_dt))
            
            #get the median of the energy, S2 and its error
            self.mean_dt = groups_dt["drift_time"].mean()/1000
            self.median_S2 = groups_dt["s2_bottom"].median()
            self.median_S2_err = np.array([1.253*sigmaS2/(counts**0.5) for sigmaS2,counts in \
                                           zip(groups_dt["s2_bottom"].std(),\
                                               groups_dt["s2_bottom"].count())])
        else:
            warnings.warn("The number of entries in data after the cut is < 3 entries")
            print("number of bins for the time is 0")
            
            return {'el_lifetime':
                    {"names"   : ["electron lifetime [us]"],
                     "values"  : [-1],
                     "errors"  : [0],
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": int(self.run_number),
                     "figures" : [None] }}
            
    	#require at least 10 entries per bin for the fit
        if (len(self.mean_dt) < 10):
            print("The number of entries in the mean of drifttime has < 10 entries, we are writing 0 in json file")
            return {'el_lifetime':
                    {"names"   : ["electron lifetime [us]"],
                     "values"  : [-1],
                     "errors"  : [0],
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": int(self.run_number),
                     "figures" : [None] }}
    
            
        
        # use iminuit to get the uncertainties (parabollic)
        mask_time = (self.mean_dt > 100) & (self.mean_dt < 750)
        
        # do a first estimation with a simple liner fit
        # Fit the data: S2_bottom vs. drift time with an exponential 
        fitfunction = np.polyfit(self.mean_dt[mask_time], np.log(self.median_S2[mask_time]), 1, full=True)

        # Fit the data: S2_bottom vs. drift time with an exponential 
        chi2 = Chi2Functor(exponential, self.mean_dt[mask_time], self.median_S2[mask_time], self.median_S2_err[mask_time])
        
        self.fitM = Minuit(chi2, tau = 1./fitfunction[0][0], alpha = np.exp(fitfunction[0][1]),\
                   error_tau = 100, error_alpha = 50,errordef = 0.1,\
                           limit_tau =(-1000,-1), print_level = 2, pedantic = True)
        
        self.fitM.migrad()
        try:
            self.fitM.hesse()
        except Exception as e:
            print("Could not get the HESSE matrix")
            raise e
        
        if not self.fitM.migrad_ok():
            print("The minimization did not take place, we are going to write 0 in the json file")
            return {'el_lifetime':
                    {"names"   : ["electron lifetime [us]"],
                     "values"  : [-1],
                     "errors"  : [0],
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": int(self.run_number),
                     "figures" : [None] }}
                        
        # if the fit succeeded then get the fit params
        else:
            tau_est = 1./fitfunction[0][0]
            s2gain_est = np.exp(fitfunction[0][1])
            self.tau = self.fitM.values['tau']
            self.tau_err = self.fitM.errors['tau']
            s2gain = self.fitM.values['alpha']
            s2gain_err = self.fitM.errors['alpha']
            self.chi2 = self.fitM.fval
            self.ndof = len(self.mean_dt)-2
            
            #Save the figure now
            self.save_electron_lifetime_figure()
            print(20*"= =")
            print ("Tau =  %.3f +- %.3f (estimation of %.3f):" %(self.tau, self.tau_err, fitfunction[0][0]))
            print ("Alpha =  %.3f +- %.3f (estimation of %.3f):" %(self.fitM.values['alpha'],\
                                                               self.fitM.errors['alpha'], fitfunction[0][1]))
            print(20*"= =")
            return {'el_lifetime':
                    {"names"   : ["electron lifetime [us]"],
                     "values"  : [-1*self.tau],
                     "errors"  : [self.tau_err],
                     "chi2"    : self.chi2,
                     "ndof"    : self.ndof,
                     "time"    : self.file_time,
                     "run_number": int(self.run_number),
                     "figures" : [os.path.basename(self.fig_name)] } }

    def save_electron_lifetime_figure(self):
        """
        produce the figure of each run for the electron lifetime that contains ELT fit
        """
        
        # make a nice plot with the results
        matplotlib.rc('font', size=16)
        plt.rcParams['figure.figsize'] = (10.0, 8.0) # resize plots
        plt.set_cmap('autumn')
        hist, binsx, binsy = np.histogram2d(self.drift_time, self.df["s2_a_bottom"],\
                                            bins=(np.linspace(self.min_time_drift, self.max_time_drift, 25),\
                                                  np.linspace(self.min_s2, self.max_s2, 25)))
        plt.pcolormesh(binsx, binsy, hist.T, norm = matplotlib.colors.LogNorm())
                
        plt.errorbar(self.mean_dt, self.median_S2, yerr = self.median_S2_err, markersize=5,\
                     marker='o', color='black', linestyle='')
        vals = [ exponential(x,**self.fitM.values) for x in self.bins_dt ]
            
        plt.plot(self.bins_dt, vals, color='black')
            
        plt.ylabel('S2 area bottom [p.e.]')
        plt.xlabel(r'Drift time [$\mu s$]')
            
        plt.figtext(0.5, 0.85, r"$\tau$ =%.2f $\pm$ %.2f [$\mu$s]" %(-self.tau, self.tau_err))
            
        plt.figtext(0.5, 0.75, r"$\chi^2$ / ndof =%.2f / %i" %(self.chi2, self.ndof))
        print("the figure name is: ", self.fig_name)    
        plt.savefig(self.fig_name, bbox_inches='tight')
        
            
        plt.close("all")
