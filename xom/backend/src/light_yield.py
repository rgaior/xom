import os
import time
import numpy as np
import scipy as sp # use it for integration
from scipy.stats import iqr as IQR
import pandas as pd
from iminuit import Minuit, describe, Struct
import matplotlib
import warnings
import matplotlib.pyplot as plt
from fitter_minuit import Chi2Functor, gaussian
from scipy.optimize import curve_fit



class LightYield(object):
    """
    - ds_s1_b_n_distinct_channels: number of PMTs contributing to s1_b distinct from the PMTs
    ds1_s1_dt: delay time between s1_a_center_time and s1_b_center_time
    ds_second_s2:  1 if selected interactions have distinct s2s 
    """
    def __init__(self,  data=None, line="cs1", energy=39, plot_file_name= None,run_number = 1234567,source="Kr"):
        """
        - Here comes the cut variables needed for this analysis
        """
        self.source = source
        self.fig_name = plot_file_name
        self.df = data
        self.energy = energy
        self.file_time = time.strftime("%Y-%m-%d %H:%M:%S", \
                                       time.localtime(self.df["time"][0]/1e9))

        # this line var. can take a or b, a would be the 9keV line, b would be 32keV line
        self.line = line
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
                # quit here because the list of variables you want to cut on has a problem:
                # maybe all variables or one does not exist in the frame
                sys.exit(1)
            
        elif self.source == "Rn":
            list_varibales_cut = ['cs1', 'cs2', 'z','r']

            if set(list_varibales_cut).issubset(self.df.columns):
                # Eliminate NaNs 
                mask_1 = (~np.isnan(self.df[list_varibales_cut[0]])) \
                         & (~np.isnan(self.df[list_varibales_cut[1]]))
                
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
                # quit here because the list of variables you want to cut on has a problem:
                #maybe all variables or one does not exist in the frame
                sys.exit(1)

   

    def get_bins(self, variable):
        """
        It calculate the binning of a given set of data, it is the best estimate
        
        use a robust method to get the binwidth: 
        https://www.fmrib.ox.ac.uk/datasets/techrep/tr00mj2/tr00mj2/node24.html
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
             

    def get_fit_parameters(self, x,y):
        """
        this function runs Minuit and migrad to obtain the fit parameters of the gaussian
        and returns a tuple of the parameters and errors: (values, errors)
        x,y: are the variables that we want to fit with Iminuit
        """
        # initial paramerts: mean:mu can't be estimated, but the sigma
        kwdargs = dict( a=y[np.argmax(y)], mu = x[np.argmax(y)], sigma=10 )
                
        # Get the Chisquare of the function that we want to fit, build the model
        # The minimization is entended to be in small range: [index_low: index_high]
        mean  = x[np.argmax(y)]
        mask  = np.abs(x - mean) <= 4*x.std()
        
        #Here a first estimate of the fit, to get the initial parameters
        gaussian_chi2 = Chi2Functor( gaussian, x[mask], y[mask], np.sqrt(y[mask]))
        iniMinuit = Minuit( gaussian_chi2, error_mu=1, error_sigma=1, errordef=1,\
                                print_level = 0, pedantic = False, **kwdargs)
                
        iniMinuit.migrad()
                
        # Now we fit all the values of y vs. x (no restriction on numb. of sigmas)         
        gaussian_chi2 = Chi2Functor(gaussian,x, y, np.sqrt(y))
                
        iniMinuit = Minuit( gaussian_chi2, error_mu=1, error_sigma=1, errordef=1,\
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
        
                
        


    def get_light_yield(self):
        """
        this is the function that calculates the light yield it returns\
        a dict: dict(light_yield, sigma)
        
        """
        
        print("The number of events in the file before the cuts: ", len(self.df))
        self.df = self.clean_data() # apply the cuts
        print("the number of events in the file is: ", len(self.df))
        if (len(self.df) < 40):
            warnings.warn("Warning the data has an entries")
            print(len(self.df) )
            warnings.warn("you can't proceed with the calculations of the light yield")
            return {'light_yield':
                    {"name"   : "light_yield",
                     "value"  : 0,
                     "error"  : 0,
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": self.run_number,
                     "pvalue"  : 0,
                     "figure" : None}} 
        


        # Now lets calculate the light yield for a given line (in Kr there are two)
        xline_s1 =  self.df["%s" % self.line]
        print(len(xline_s1))
        nbins = self.get_bins(xline_s1)
        print("number of bins: ", nbins)
        bins_x = np.linspace( xline_s1.min(),xline_s1.max(), nbins)
        
        # group the data to get the x, y values to be fitted with minuit
        groups_s1 = self.df.groupby(np.digitize(xline_s1, bins_x))
        x = groups_s1["%s" % self.line].mean()
        y = groups_s1["%s" % self.line].count()
        
        # lets see if there are NaNs in x, y after we have grouped them
        mask_nans = (~np.isnan(x)) & (~np.isnan(y))
        x = x[mask_nans]
        y = y[mask_nans]
        ndof = len(x) - 3 # the gaussian has 3 parameters

        print("the length of the data after the cuts:%i" % len(x))
        
        fitParameters, fitErrors,chi2 = self.get_fit_parameters(x.values, y.values)
        print("The fit parameters: ", fitParameters, fitErrors, chi2/ndof)
        
        if fitParameters["mu"] == 0:
            print("the fit did not converge for this data")
            return {'light_yield':
                    {"name"   : "light_yield",
                     "value"  : 0,
                     "error"  : 0,
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": self.run_number,
                     "pvalue"  : 0,
                     "figure" : None}} 
        else:
            #calculate the p-value of the fit for a given ndof and a chisqr
            pvalue = 1 - sp.stats.chi2.cdf(x=chi2,  df=ndof) # Find the p-value
            print("save now the figure %s" %self.fig_name)
            self.save_figure(x.values, y.values,fitParameters,fitErrors,\
                                         self.fig_name, chi2, ndof)
                
            return {'light_yield':
                    {"name"   : "light_yield",
                     "value"  : fitParameters["mu"]/self.energy,
                     "error"  : fitErrors["mu"]/self.energy,
                     "chi2"    : chi2,
                     "ndof"    : ndof,
                     "time"    : self.file_time,
                     "run_number": self.run_number,
                     "pvalue"  : "%.1f" % (pvalue*100),
                    "figure" : os.path.basename(self.fig_name) }}                

    def save_figure(self, x,y,fitparameters,errfitparameters,filename, chi2, ndof):
        """
        return the figure that shows the fit on top of the light yield
        the fit parameters are given as dictionary
        """

        matplotlib.rc('font', size=16)
        plt.rcParams['figure.figsize'] = (10.0, 8.0)
        plt.errorbar(x,y, yerr = np.sqrt(y),markersize=5,\
                     marker='o', color='black', linestyle ="")

        #plot between 2sigmas the fitted plot
        x = np.linspace(x.min(), x.max(), 200) 
        mask = (x > (fitparameters["mu"] -6 *fitparameters["sigma"])) &\
               ( x < (fitparameters["mu"] + 6 *fitparameters["sigma"]))

        plt.plot(x[mask],gaussian(x[mask],**fitparameters),"r-",linewidth=2.5)


        plt.figtext(0.47,0.85,r"Light Yield =(%.4f $\pm$ %.4f)[p.e/keV] "%\
                    (fitparameters["mu"]/self.energy,\
                    errfitparameters["mu"]/self.energy), color="r", fontsize=15)

        plt.figtext(0.47,0.8,r"$\sigma_{LY}$ = (%.4f $\pm$ %.4f)[p.e/keV]" %\
                    (fitparameters["sigma"]/self.energy,\
                     errfitparameters["sigma"]/self.energy),color="r",fontsize=15)
        plt.figtext(0.47,0.75,r"$\chi_{LY}$/ndof = (%.4f/%i)" %(chi2,ndof)\
                    , color="g", fontsize=15)                                                    

        plt.xlabel("Cs1 area [p.e]")
        plt.ylabel("Number of Entries")
        plt.savefig(filename, bbox_inches = "tight")
        plt.close("all")
        return 0

    
