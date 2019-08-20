from iminuit import Minuit, describe
from iminuit.util import make_func_code
import math
import numpy as np
#This helper class I have stolen from: http://nbviewer.jupyter.org/github/iminuit/iminuit/blob/master/tutorial/

class Chi2Functor:
    def __init__(self,f,x,y,yerr):
        self.f = f
        self.x = x
        self.y = y
        self.yerr = yerr
        f_sig = describe(f)
        #this is how you fake function
        #signature dynamically
        self.func_code = make_func_code( f_sig[1:] )#docking off independent variable
        self.func_defaults = None #this keeps np.vectorize happy

    def __call__(self,*arg):
        #notice that it accept variable length
        #positional arguments
        chi2 = sum( ( y - self.f(x,*arg) )**2 / yerr**2  for x,y,yerr in zip(self.x,self.y,self.yerr))
    #    if math.isnan(chi2):
    #        print(self.yerr)


        return chi2

def exponential(x, alpha, tau):
    """
    an exponential decay that can be used for the electron life time
    """
    return alpha * np.exp(1./tau*x)

def exponential_plus_const(x, alpha, tau,ct):
    """
    an exponential decay that can be used for the electron life time
    """
    return alpha * np.exp(1/tau *x) + ct

def gaussian(x, a, mu, sigma):
    """
    The gaussian function that we want to fit to the energy to obtain the light yield
    """
    return a * np.exp(-(x - mu) ** 2 / 2. / sigma ** 2)
