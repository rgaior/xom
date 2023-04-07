#needed for xom_saver:
import os
from doctest import run_docstring_examples
import sys
import json
#from bson.json_util import dumps
import constant
import subprocess
import dblib as dbl
import influxdb_client

## figure folder on the machine that host the database and display (grafana)
#display_fig_folder = "/home/xom/data/v1.1/test/." 

measurement_data_name = constant.measurement_name

class Xomresult:
    def __init__(self,
                 analysis_name,
                 analysis_version, 
                 variable_name, 
                 variable_value,        
                 runid,
                 measurement_name = measurement_data_name, 
                 container=None,
                 runids = [""],
                 timestamp = 0,
                 data=None, 
                 figure_path="",
                 tag = ""
             ):
        self.measurement_name = measurement_name
        self.analysis_name = analysis_name
        self.analysis_version = analysis_version
        self.variable_name = variable_name
        self.variable_value = variable_value
        self.runid = runid
        if container == None:
            self.container = os.getenv('SINGULARITY_NAME')
        else:
            self.container = container
        self.runids = runids
        self.timestamp = timestamp
        self.data = data
        self.figure_path = figure_path
        self.tag = tag
        self.result_dict = self.set_result_dict()
        '''
        analysis_name: str
        variable_name: str
        analysis_version: str
        variable_value: float
        runid: int
        container : str (name of the container)
        runids : list of runids
        timestamp : int
        data format is a dictionnary {"key":value, }
        figure_path : str
        tag:analysis specific tag
        '''

    def set_result_dict(self):
        self.result_dict = {"measurement_name":self.measurement_name, "analysis_name": self.analysis_name, "analysis_version": self.analysis_version, "variable_name": self.variable_name, "variable_value": self.variable_value, "runid":self.runid, "container": self.container, "runids":self.runids, "timestamp": self.timestamp, "data":self.data, "figure_path":self.figure_path, "tag":self.tag}
        


    def get_result_records(self):
        record_list = []
        if self.result_dict is None:
            self.set_result_dict()
        result = self.result_dict
        runids = "_".join(self.runids) 

        pmain = influxdb_client.Point(self.measurement_name).field(result['variable_name'], result['variable_value']).tag("datatype", "main").tag("analysis_name", result['analysis_name']).tag("analysis_version", result['analysis_version']).tag("variable_name",result['variable_name']).field("runid", result['runid']).tag("container",result['container']).field("runids",runids).field("timestamp",result['timestamp']).field("figure_path",result['figure_path']).tag("tag",result['tag'])
        record_list.append(pmain)
        if isinstance(self.result_dict['data'], dict):
            for key, val in self.result_dict['data'].items():
                if isinstance(val, np.ndarray):
                    for v in val:
                        p = influxdb_client.Point(self.measurement_name).field(result['variable_name'], result['variable_value']).tag("datatype", "extra").tag("analysis_name", result['analysis_name']).tag("analysis_version", result['analysis_version']).tag("variable_name",result['variable_name']).field("runid", result['runid']).tag("container",result['container']).field("runids",runids).field("timestamp",result['timestamp']).field("figure_path",result['figure_path']).tag("tag",result['tag']).field(key,v)
                        record_list.append(p)
                else:
                    p = influxdb_client.Point(self.measurement_name).field(result['variable_name'], result['variable_value']).tag("datatype", "extra").tag("analysis_name", result['analysis_name']).tag("analysis_version", result['analysis_version']).tag("variable_name",result['variable_name']).field("runid", result['runid']).tag("container",result['container']).field("runids",runids).field("timestamp",result['timestamp']).field("figure_path",result['figure_path']).tag("tag",result['tag']).field(key,val)
                
                    record_list.append(p) 

        return record_list

    def query_from_result(self):
        query = 'from(bucket:"xom")|> range(start: '+ str(-constant.query_period) + 'd) |> filter(fn: (r) => r._measurement ==  \"' + self.measurement_name + '\") |> filter(fn: (r) => r.analysis_name == \"' + self.analysis_name + '\") |> filter(fn: (r) => r.variable_name == \"' + self.variable_name + '\") |> filter(fn: (r) => r.analysis_version == \"' + self.analysis_version + '\") |> filter(fn: (r) => r.runid == \"' + self.runid + '\") '
        print("query = ", query)
        if dbl.query(query) is None:
            print("XOM_ERROR")
        else:
            print("XOM_OK")


    def save_in_db(self, record):
        ## connect to the database:
        client = dbl.Xomdb('influxdb',self.measurement_name)
        client.insert_record(record)

#    def test_if_written(self, record):
        
    def save(self):
        record = self.get_result_records()
        self.save_in_db(record)
        

            
# def xom_saver(        
#         analysis_name, var_name, runid, var_value,
#         runids = None,
#         timestamp = None,
#         data=None, 
#         figure=None,
#         datatype = None,
#         tag = None,
#         save_folder = None,
#         db = 'influxdb'
# ):
#     """ simple function to save results in xom fomat 
#     :param analysis_name: name of the variable of the analysis 
#     :param runids: optional array for several run ids
#     :param var_name: name of the variable of the analysis 
#     :param var_value: variable you want to display
#     :param timestamp: 
#     :param data: additionnal array of data (can be either [val, error, chi2] , can be [x1, x2, x3 ..., x10] bin content etc) 
#     :param figure: figure object one want to display in the xom display
#     :param tag: analyse specific tag
#     :param save_folder: folder to save the json data in 
    
#     """
#     # server_address = constant.server_address
#     if save_folder == None:
#         save_folder = constant.output_folder + './tmp/' 
    
#     container = os.getenv('SINGULARITY_NAME')

#     result = {}
#     result['analysis_name'] = analysis_name
#     if timestamp:
#         result['timestamp'] = int(timestamp/1e9)
#     result['runid'] = int(runid)
#     result['var_name'] = var_name
#     result['container'] = container
#     result['value'] = var_value
#     result['tag'] = tag
#     result['type'] = datatype
#     result['data'] = data
    
#     ## standard json filename to be written in case the database connections fails
#     outfname = result['analysis_name']+ "_" + result['var_name']+'_'+str(result['runid']) +  '_' + result['container']
#     outjsonname = outfname +'.json'
#     ## save the JSON file on disk    
#     filename = save_folder + outjsonname
#     with open(filename,'w') as f:
#         json.dump(result,f)
#         f.close()

#     ## save the figure 
#     if figure:
#         figname = 'fig_' + result['var_name']+'_'+str(result['runid']) +  '_' + 'cont_' + result['container'] + '_' + tag +'.png'
#         figpath = save_folder + figname
#         figure.savefig(figpath)

    
    
#     #check if written
    
#     return True
    

# def xom_message(sucess):
#     if sucess == True:
#         print("PROCESSEDWITHXOM")
#     if sucess == False:
#         print("ERRWITHXOM")

#     # # copy fig somewhere, for the moment at LNGS
#     # process = subprocess.Popen(['scp', figpath, 'xom@xe1t-offlinemon.lngs.infn.it:'+ display_fig_folder], 
#     #                        stdout=subprocess.PIPE,
#     #                        universal_newlines=True)
  
 
