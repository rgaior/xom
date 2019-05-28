import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import time
import numpy as np
import scipy as sp # use it for integration
from scipy.stats import iqr as IQR
import pandas as pd
from matplotlib.colors import LogNorm
from iminuit import Minuit, describe, Struct
import matplotlib
import warnings
import matplotlib.pyplot as plt
from fitter_minuit import Chi2Functor, gaussian
from scipy.optimize import curve_fit



class ChargeYield():
    """
    - ds_s1_b_n_distinct_channels: number of PMTs contributing to s1_b distinct from the PMTs
    ds1_s1_dt: delay time between s1_a_center_time and s1_b_center_time
    ds_second_s2:  1 if selected interactions have distinct s2s 
    """
    def __init__(self,  line, energy, data, source="Kr", cut = True, correction = True):
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
        self.s2_a_max_cut = 1e5
        self.source = source
        self.energy = energy
        self.line = line
        self.cut = cut
        self.file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.df["event_time"][0]/1e9))
        self.run_number = int(self.df["run_number"][0])
        self.list_variables_cut = ['ds_s1_b_n_distinct_channels','ds_s1_dt','s2_a', 's2_b', \
                                   'cs1_a', 'cs1_b', 'cs2_a','int_a_r_3d_nn', 'int_a_z_3d_nn']
        
    def clean_data(self):
        """
        Apply the cuts to the data through this function
        1 - Time cut between s10 and s11
        2 - Energy cut for s10& s11 and s20
        """
        if self.source == "Kr":
            if self.cut:
                #check if the cut list variables is included inside the dataframe
                if set(self.list_variables_cut).issubset(self.df.columns):
                    mask_1 = ~np.isnan(self.df[self.list_variables_cut[6]])
                    mask_2 = (self.df[self.list_variables_cut[7]] < self.tpc_radius_cut)
                    mask_3 = (self.df[self.list_variables_cut[6]] < self.s2_a_max_cut )
                    self.df = self.df[mask_1 & mask_2 & mask_3]
                else:
                    print("One of the varibales in the list", list_variables_cut)
                    print("Does not exists in the data frame")
                    warnings.warn('The data is not going to be cleaned')
            else:
                warnings.warn('YOU CHOOSE NOT TO HAVE THE CUTS APPLIED TO DATA')
                warnings.warn('The data is not cleaned')
                        
                #elif self.source == "Rn":
                #    if self.cut:
                #        "print we are going to get here the cuts"
        return self.df


    def get_fit_parameters(self, x,y):
        """
        this function runs Minuit and migrad to obtain the fit parameters of the gaussian
        and returns a tupe of the parameters and errors: (values, errors)
        data: is the histogram that we want to fit to a gaussian
        make use of the np.histogram to get the (x,y) values of the distribution
        range where the histgrom should be plotted is in the range=binrage, that is a tuple
        """
        # initial paramerts: mean:mu can't be estimated, but the sigma
        kwdargs = dict( a=y[np.argmax(y)], mu = x[np.argmax(y)], sigma=np.std(x) )
                
        # Get the Chisquare of the function that we want to fit, build the model
        # The minimization is entended to be in small range: [index_low: index_high]
        mean  = x[np.argmax(y)]
        mask  = np.abs(x - mean) <= 0.95*x.std() 
        #popt, pcov= curve_fit(gaussian,x[mask], y[mask], p0 =[1000,250, 20],sigma=np.sqrt(y[mask]),absolute_sigma=True)
        #print("curveFit: ", popt)
        
        
        gaussian_chi2 = Chi2Functor( gaussian, x[mask], y[mask], np.sqrt(y[mask]))
        iniMinuit = Minuit( gaussian_chi2, error_mu=1000, error_sigma=1000, errordef=1,\
                                print_level = 0, pedantic = False, **kwdargs)
                
        iniMinuit.migrad()
                
        mask = ( x > iniMinuit.values["mu"] - 6*iniMinuit.values["sigma"]) &\
               ( x < iniMinuit.values["mu"] + 6*iniMinuit.values["sigma"])
                
        gaussian_chi2 = Chi2Functor(gaussian,x, y, np.sqrt(y))
                
        iniMinuit = Minuit( gaussian_chi2, error_mu=1000, error_sigma=1000, errordef=1,\
                            print_level = 0, pedantic = False , **iniMinuit.values)

        
        iniMinuit.migrad()
        if not iniMinuit.migrad_ok():
            print("migrad was not ok")
            for k in iniMinuit.values.keys():
                iniMinuit.values[k] = 0
                iniMinuit.errors[k] = 0

        else:
            iniMinuit.hesse()
            print("The fit values: ", iniMinuit.values)
            print ("The chisqr: ")
            print(iniMinuit.fval)
            
            
                 
        return (iniMinuit.values, iniMinuit.errors, iniMinuit.fval)
        
                
        
    def get_x_y(self, data, variable):
        """
        returns the x,y of a given histgram for a given variable that I name: dataframe
        """
        xInitial = data["%s" %variable]
        print("min max of x: ", np.min(xInitial), np.max(xInitial))
        
        binwidth = 2*IQR(xInitial)*(len(xInitial)**(-1/3))
        if binwidth == 0:    
            print("the value of the binwidth:", binwidth)
            print("the binwidth is 0, check this file")
            return None, None
    
        else:
            nbins = int( (xInitial.max() - xInitial.min())/binwidth )
            if nbins:
                print("NBINS: ", nbins, binwidth)
                bins_x = np.linspace(xInitial.min()-1,  xInitial.max() +1, nbins)
                print(20*"§§")
                print("these are the bins on x: ", len(bins_x), bins_x[0], bins_x[-1])
                print(20*"§§")
                groups_s2 = data.groupby(np.digitize(data["%s" %variable], bins_x))
                x = groups_s2["%s" % variable].mean()
                y = groups_s2["%s" % variable].count()
        
                return x.values, y.values
            else:
                return None, None
        
    def get_charge_yield(self, plot_file_name, tbins = 10):
        """
        this is the function that calculates the light yield it returns a dict: dict(light_yield, sigma)
        It uses the corrected Cs1
        This function gets bins of time between s10 and s20 (s1a, s1b), tbins 
        """
        print("THIS IS THE FILE NAME OF THE PLOT:%s" % plot_file_name)
        if self.cut:
            print("The number of events in the file before the cuts: ", len(self.df))
            #apply the cuts
            self.df = self.clean_data() # apply the cuts
            print("the number of events in the file is: ", len(self.df))
            
            if (len(self.df) < 10):
                warnings.warn("Warning the data has an entries")
                print(len(self.df) )
                warnings.warn("you can't proceed with the calculations of the charge yield")
                return {'charge_yield':
                        {"names"   : ["charge_yield"],
                         "values"  : 0,
                         "errors"  : 0,
                         "chi2"    : 0,
                         "ndof"    : 0,
                         "time"    : self.file_time,
                         "run_number": self.run_number,
                         "pvalue"  : 0,
                        "figures" : [None]}} 
        else:
            warnings.warn('YOU CHOOSE NO TO HAVE THE CUTS APPLIED TO DATA')
            warnings.warn('The CHARGE YILED MAY NOT BE OK: CHECK it first')
        #use a robust method to get the binwidth:
        #https://www.fmrib.ox.ac.uk/datasets/techrep/tr00mj2/tr00mj2/node24.html

        #HERE COMES THE LOOP OVER TIME, FOR EACH BIN ONE WOULD GET ONE VALUE OF THE LIGHT YIELD
        #AT THE END ONE SHOULD TAKE INTO CONSIDERATION IN EACH BIN OF TIME TO HAVE AT LEAST ONE VALUE
        #THAT IS HAS MEANINGFULL VALUE OTHERWISE RETURN ALL WITH 0 as ACHARGE YIELD

        self.charge_yield_all_bins = dict()
        #create a non linear time bins spacing
        self.bin_t = np.logspace(np.log10(self.dtmin_cut),np.log10(self.dtmax_cut),tbins)
        for i in range(len(self.bin_t)-1):
            
            mask_t = (self.df[self.list_variables_cut[1]]> self.bin_t[i]) \
                     & (self.df[self.list_variables_cut[1]]< self.bin_t[i+1])
            print(20*"_-")
            print("we are at ith %i"%i, len(self.df[self.line][mask_t]) )
            print(20*"-_")
            if len(self.df[self.line][mask_t]) < 2: # it is the same as the number of fit parameters:
                print("the Original data has a len <2, for the bin %i" %i)
                self.charge_yield_all_bins[i] = { "values"  : 0,
                                             "errors"  : 0}
                continue
            
            x,y = self.get_x_y(self.df[mask_t], self.line)
            
            if x is None:
                print("the binwidth is 0, check this file")
                self.charge_yield_all_bins[i] = { "values"  : 0,
                                             "errors"  : 0}
                continue
            elif len(x) < 6: #(2 times the number of fit parameters)
                print("the lenght of data in this bin: %i" %i, "is < 6", len(x))
                print("I am going to go to the next value")
                self.charge_yield_all_bins[i] = { "values"  : 0,
                                             "errors"  : 0}
                continue
            ndof = len(x) - 3 # the gaussian has 3 parameters
                
            print("the length of the data after the cuts:%i" % len(x))
            #popt, pcov = curve_fit(gaussian,x, y, p0=[y[y.argmax()], x[y.argmax()], 100], sigma=np.sqrt(y))
            #fitParameters = {"a":popt[0], "mu":popt[1], "sigma":popt[2]}
            #fitErrors, pval, chi2 = self.chi_calc(gaussian, x, y, np.sqrt(y), popt, pcov)

        
            fitParameters, fitErrors,chi2 = self.get_fit_parameters(x, y)
            print("The fit parameters: ", fitParameters, "errors:", fitErrors, "chi, pval", chi2/ndof)#, pval)
        
            if fitParameters["mu"] == 0:
                print("the fit did not converge for this data")
                self.charge_yield_all_bins[i] = { "values"  : 0,
                                             "errors"  : 0}
                continue
                
            else:
                #calculate the p-value of the fit for a given ndof and a chisqr
                pvalue = 1 - sp.stats.chi2.cdf(x=chi2,  df=ndof) # Find the p-value
                
                #self.save_light_yield_figure(x.values, y.values,fitParameters,fitErrors,plotfilename, chi2, ndof)
                self.charge_yield_all_bins[i] = { "values"  : fitParameters["mu"],
                                             "errors"  : fitErrors["mu"]}
                
        # here we are going to perform another fit
        # The fit here is about all the values that we get from each bin of time
        # We fit it again with a gaussian
        # Of course the object to perform the calc on is: charge_yield_all_bins
        mean_charge = list()
        error_charge = list()
        for i,v in enumerate(self.charge_yield_all_bins.values()):
            print("the values len: ", v)
            if v["values"]!=0:
                mean_charge.append(v["values"])
                error_charge.append(v["errors"])
            else:
                print("The ith %i bin for which there is no value:" %i)
        # now lets calculate the mean of the means
        # Calculate the error bar on the mean by using the sum^2 of the errors
        print("the values are:", mean_charge)
        charge_yield = np.mean(mean_charge)
        standard_error = np.sqrt(np.sum([error_charge[i]**2 for i in range(len(error_charge))] ) / len(error_charge))
        x_disp = self.df[self.list_variables_cut[1]]
        y_disp = self.df[self.line]
        mask  = self.df[self.list_variables_cut[1]] < 2000
        self.save_light_yield_figure(x_disp.values[mask], y_disp.values[mask], plot_file_name)
        return {'charge_yield':
                {"names"   : ["charge_yield"],
                 "values"  : charge_yield/self.energy,
                 "errors"  : standard_error/self.energy,
                 "chi2"    : 0,
                 "ndof"    : 0,
                 "time"    : self.file_time,
                 "run_number": self.run_number,
                 "pvalue"  : 0,
                "figures" : [os.path.basename(plot_file_name)]}}
                                

    def save_light_yield_figure(self, x,y,filename):
        """
        return the figure that shows the fit on top of the light yield
        the fit parameters are given as dictionary
        """

        matplotlib.rc('font', size=16)
        plt.rcParams['figure.figsize'] = (10.0, 8.0)
        plt.hist2d(x,y, bins = 40, norm=LogNorm())
        time_bins = self.bin_t[:-1] + np.diff(self.bin_t)/2
        y_bins = [ v["values"] for v in self.charge_yield_all_bins.values() ]
        y_err  = [ v["errors"] for v in self.charge_yield_all_bins.values() ]
        plt.errorbar(time_bins,y_bins, yerr = y_err,markersize=5, marker='o', color='red', linestyle ="")


        #plot between 2sigmas the fitted plot
        #x = np.linspace(x.min(), x.max(), 200) 
        #mask = (x > (fitparameters["mu"] -6 *fitparameters["sigma"])) &( x < (fitparameters["mu"] \
        #                                                                      + 6 *fitparameters["sigma"]))

        #plt.plot(x[mask],gaussian(x[mask],**fitparameters),"r-",linewidth=2.5)


        #plt.figtext(0.47,0.85,r"Light Yield =(%.4f $\pm$ %.4f)[p.e/keV] " %(fitparameters["mu"]/self.energy,
        #                                                               errfitparameters["mu"]/self.energy), color="r", fontsize=15)

        #plt.figtext(0.47,0.8,r"$\sigma_{LY}$ = (%.4f $\pm$ %.4f)[p.e/keV]" %(fitparameters["sigma"]/self.energy,

         #                                                               errfitparameters["sigma"]/self.energy),color="r",fontsize=15)
        #plt.figtext(0.47,0.75,r"$\chi_{LY}$/ndof = (%.4f/%i)" %(chi2,ndof), color="g", fontsize=15)

                                                                        

        plt.xlabel("time [ns]")
        plt.ylabel("S2_bottom")
        plt.savefig(filename, bbox_inches = "tight")
        plt.close("all")
        return 0

    def chi_calc(self, model_func,x_data,y_data,y_err,params,covariance):
        """
        caluclate the chi_square/ndof
        calculate the correlation coefficient
        """
        fit_params_dict = dict()
        fit_error_dict = dict()
        print ("\nNumber of Data Points = %i, Number of Parameters = %1i" % (len(x_data), len(params) ))

        print ("Covariance Matrix : \n", covariance, "\n")
        dof = len(x_data) - len(params)
        print ("Correlation Matrix :")
        for i,row in enumerate(covariance):
            for j in range(len(params)) :
                print ("%10f"%(covariance[i,j]/np.sqrt(covariance[i,i]*covariance[j,j])))

        # Calculate Chi-squared
        chisq = sum(( ( y_data - model_func(x_data,*params)) / y_err )**2)
    

        print ( "\nEstimated parameters and uncertainties (with initial guesses)")
        for i in range(len(params)) :
            print ("   p[%d] = %0.3e +/- %0.3e" % (i,params[i],covariance[i,i]**0.5*max(1,np.sqrt(chisq/dof))))

        print ( "Chi-Squared/dof = %10.5f, CDF = %10.5f%%" % (chisq/dof, 100.*float(sp.special.chdtrc(dof,chisq))))
        
        err0 = covariance[0,0]**0.5 * max(1,np.sqrt(chisq/dof))
        err1 = covariance[1,1]**0.5 * max(1,np.sqrt(chisq/dof))
        err2 = covariance[2,2]**0.5 * max(1,np.sqrt(chisq/dof))
        
        fit_error_dict = { 'a':err0,'mu':err1,'sigma':err2}
                     
        pval = 100.*float(sp.special.chdtrc(dof,chisq))
        if chisq > dof :
            print ("Because Chi-squared > dof, the parameter uncertainty")
            print ("      estimates have been scaled up by Chi-squared/dof.")
            print ("the error on p[0] was %0.3e and after scaling %0.3e"%(covariance[0,0]**0.5,err0))
            print ("the error on p[1] was %0.3e and after scaling %0.3e"%(covariance[1,1]**0.5,err1))
            print ("the error on p[2] was %0.3e and after scaling %0.3e"%(covariance[2,2]**0.5,err1))

        return fit_error_dict, pval, chisq 
