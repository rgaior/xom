import os
import sys
import numpy as np 
import pandas as pd
from tqdm import tqdm
from glob import glob
import pickle
import hax
from hax import cuts
from pax import configuration, units, datastructure


class GetDataFrame():
    
    """this class uses hax to read the a given minitree and returns back the corresponding pandas data frame"""

    def __init__(self, run_number= None , minitree_name="", pax_version="", directory="" ):
        """Get the minitree name corresponding to runnumber and processed with a given pax_version"""
        self.pax_version = pax_version
        self.run_number = run_number
        self.minitree   = minitree_name
        self.directory  = directory 
        
    def get_df(self):
        """ make use of hax and get the data frame """
        if (self.pax_version!="") and (self.run_number != None) and (self.minitree != "") and (self.directory!=""):
            # here combine the subdirectory with the pax version
            main_directory = self.directory + "/" + self.pax_version
            if os.path.exists("%s" % main_directory):

                # lets call now hax and process the minitrees
                hax.init(experiment='XENON1T', minitree_paths =["%s" % main_directory],\
                         #main_data_paths=['/project2/lgrandi/xenon1t/processed/%s/'%pax_version],\
                         detector='tpc')
                    
                return hax.minitrees.load([self.run_number],["%s" % self.minitree,"Basics", "Fundamentals"])
            else:
                print("the path: %s" % main_directory)
                print("does not exists")
                print("the class GetDataFrame is going to quit here")
                sys.exit(0)
        else:
            print("Make sure that the arguments you give to the class GetDataFrame are all ok")
            print("The run_number: ", self.run_number)
            print("The tree name: ", self.minitree)
            print("The directory: ", self.dierctory)
            print("the class GetDataFrame is going to quit here")

            sys.exit(0)

