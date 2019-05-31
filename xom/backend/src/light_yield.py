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
    def __init__(self,  line, energy, data, source="Kr"):
        """
        - Here comes the cut variables needed for this analysis
        """
        self.correction = correction
        self.df  = data
        self.tpc_length = 96.9
        self.tpc_radius = 47.9
        self.zmin_cut = -92.9
        self.zmax_cut = -9
        self.tpc_radius_cut = 36.94
        self.dtmin_cut = 500
        self.dtmax_cut = 2000
        self.nPmts_min = 3
        self.nPmts_max = 30
        self.s1_0_min_cut = 50
        self.s1_0_max_cut = 700
        self.s1_1_min_cut = 30
        self.s1_1_max_cut = 500
        self.s2_0_min_cut = 100
        self.source = source
        self.energy = energy
        self.line = line
        self.cut = cut
        self.file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.df["event_time"][0]/1e9))
        self.run_number = int(self.df["run_number"][0])
        
        
    def clean_data(self):
        """
        Apply the cuts to the data through this function
        1 - Time cut between s10 and s11
        2 - Energy cut for s10& s11 and s20
        """
        if self.source == "Kr":
        
            list_varibales_cut = ['ds_s1_b_n_distinct_channels','ds_s1_dt','s2_a', 's2_b', 'cs1_a',\
                                      'cs1_b', 'cs2_a','int_a_r_3d_nn', 'int_a_z_3d_nn']
            if set(list_varibales_cut).issubset(self.df.columns):
                mask_1 = (self.df[list_varibales_cut[0]] < self.nPmts_max) &\
                         (self.df[list_varibales_cut[0]] > self.nPmts_min) &\
                         (self.df[list_varibales_cut[1]] > self.dtmin_cut) &\
                         (self.df[list_varibales_cut[1]] < self.dtmax_cut) &\
                         (self.df[list_varibales_cut[2]] == self.df[list_varibales_cut[3]])
                            
                mask_2  =  (self.df[list_varibales_cut[4]] < self.s1_0_max_cut) &\
                           (self.df[list_varibales_cut[4]] > self.s1_0_min_cut) &\
			   (self.df[list_varibales_cut[5]] < self.s1_1_max_cut) &\
                           (self.df[list_varibales_cut[5]] > self.s1_1_min_cut) &\
			   (self.df[list_varibales_cut[6]] > self.s2_0_min_cut)
                                
                                
                mask_3 = (self.df[list_varibales_cut[7]] < self.tpc_radius_cut) &\
                         (self.df[list_varibales_cut[8]] < self.zmax_cut) &\
			 (self.df[list_varibales_cut[8]] > self.zmin_cut)
                   
                             
                return self.df[mask_1 & mask_2 & mask_3]
            else:
                print("One of the varibales in the list", list_varibales_cut)
                print("Does not exists in the data frame")
                warnings.warn('The data is not going to be cleaned')
                sys.exit(1)
        elif self.source == "Rn":
                list_varibales_cut = ['ds_s1_b_n_distinct_channels','ds_s1_dt','s2_a', 's2_b', 'cs1_a',\
                                      'cs1_b', 'cs2_a','int_a_r_3d_nn', 'int_a_z_3d_nn']
            if set(list_varibales_cut).issubset(self.df.columns):
                mask_1 = (self.df[list_varibales_cut[0]] < self.nPmts_max) &\
                         (self.df[list_varibales_cut[0]] > self.nPmts_min) &\
                         (self.df[list_varibales_cut[1]] > self.dtmin_cut) &\
                         (self.df[list_varibales_cut[1]] < self.dtmax_cut) &\
                         (self.df[list_varibales_cut[2]] == self.df[list_varibales_cut[3]])
                            
                mask_2  =  (self.df[list_varibales_cut[4]] < self.s1_0_max_cut) &\
                           (self.df[list_varibales_cut[4]] > self.s1_0_min_cut) &\
			   (self.df[list_varibales_cut[5]] < self.s1_1_max_cut) &\
                           (self.df[list_varibales_cut[5]] > self.s1_1_min_cut) &\
			   (self.df[list_varibales_cut[6]] > self.s2_0_min_cut)
                                
                                
                mask_3 = (self.df[list_varibales_cut[7]] < self.tpc_radius_cut) &\
                         (self.df[list_varibales_cut[8]] < self.zmax_cut) &\
			 (self.df[list_varibales_cut[8]] > self.zmin_cut)
                   
                             
                return self.df[mask_1 & mask_2 & mask_3]
            else:
                print("One of the varibales in the list", list_varibales_cut)
                print("Does not exists in the data frame")
                warnings.warn('The data is not going to be cleaned')
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
    
    def get_rid_nans(self, variable):
        """
        In this function we look for nans and get rid of them
        - We need to check first the percentage of NaNs in this variable
        - If the number of NaNs is > 30% of the total data then we stop even calculating the light yield  
        
        """
        where_are_NaNs = np.isnan(variable)
        if len(where_are_NaNs)/len(variable)<0.3: 
            return variable[~np.isnan(variable)]
        else:
            # here we are going to stop the whole class
            nings.warn("Warning the data has more than 30% of NaNs, check it !!!")
            sys.exit(1)
        
        return variable

    def get_fit_parameters(self, x,y):
        """
        this function runs Minuit and migrad to obtain the fit parameters of the gaussian
        and returns a tupe of the parameters and errors: (values, errors)
        data: is the histogram that we want to fit to a gaussian
        make use of the np.histogram to get the (x,y) values of the distribution
        range where the histgrom should be plotted is in the range=binrage, that is a tuple
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
        
                
        


    def get_light_yield(self, plot_file_name):
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
                    {"names"   : ["light_yield"],
                     "values"  : 0,
                     "errors"  : 0,
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": self.run_number,
                     "pvalue"  : 0,
                     "figures" : [None]}} 
        


        # Now lets calculate the light yield for a given line (in Kr there are two)
        xline_s1 =  self.df["%s" % self.line]
        
        nbins = self.get_bins(xline_s1)
        print("number of bins: ", nbins)
        bins_x = np.linspace( xline_s1.min(),xline_s1.max(), nbins)
        
        # group the data to get the x, y values to be fitted with minuit
        groups_s1 = self.df.groupby(np.digitize(xline_s1, bins_x_s1))
        x = groups_s1["%s" % self.line].mean()
        y = groups_s1["%s" % self.line].count()
        ndof = len(x) - 3 # the gaussian has 3 parameters

        # lets see if there are NaNs in x, y after we have grouped them
        x = self.get_rid_nans(x)
        y = self.get_rid_nans(y)
        
        print("the length of the data after the cuts:%i" % len(x))
        
        fitParameters, fitErrors,chi2 = self.get_fit_parameters(x.values, y.values)
        print("The fit parameters: ", fitParameters, fitErrors, chi2/ndof)
        
        if fitParameters["mu"] == 0:
            print("the fit did not converge for this data")
            return {'light_yield':
                    {"names"   : ["light_yield"],
                     "values"  : 0,
                     "errors"  : 0,
                     "chi2"    : 0,
                     "ndof"    : 0,
                     "time"    : self.file_time,
                     "run_number": self.run_number,
                     "pvalue"  : 0,
                     "figures" : [None]}} 
        else:
            #calculate the p-value of the fit for a given ndof and a chisqr
            pvalue = 1 - sp.stats.chi2.cdf(x=chi2,  df=ndof) # Find the p-value
            print("save now the figure %s" %plot_file_name)
            self.save_light_yield_figure(x.values, y.values,fitParameters,fitErrors,\
                                         plot_file_name, chi2, ndof)
                
            return {'light_yield':
                    {"names"   : ["light_yield"],
                     "values"  : [ fitParameters["mu"]/self.energy],
                     "errors"  : [fitErrors["mu"]/self.energy],
                     "chi2"    : chi2,
                     "ndof"    : ndof,
                     "time"    : self.file_time,
                     "run_number": self.run_number,
                     "pvalue"  : "%.1f" % (pvalue*100),
                    "figures" : [os.path.basename(plot_file_name)] }}                

    def save_light_yield_figure(self, x,y,fitparameters,errfitparameters,filename, chi2, ndof):
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

    
