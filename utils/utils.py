import configparser
import shlex
import subprocess
import constant
import locklib as ll
import dblib as dbl
import importlib
import os


def get_xom_config(configname='xomconfig.cfg'):
    xomconfig = configparser.ConfigParser()
    xomconfig.sections()
    configfilename = configname
    xomconfig.read(constant.xomfolder + '/utils/' + configfilename)
    print(xomconfig.sections())
    return xomconfig

def get_from_config(xomconfig, analysis_name, item_to_return):
#    logger.info('set up config with file %s: ', constant.configname)
    analysis_names = xomconfig.sections()
    print(analysis_names)
    if analysis_name not in analysis_names:
        print("error in analyis name")
    else:
        if xomconfig.has_option(analysis_name,item_to_return):
            item_returned  = xomconfig.get(analysis_name,item_to_return)
            if item_to_return in ['exclude_tags', 'include_tags', 'container', 'available_type']:
                item_returned = item_returned.split(',')

            return item_returned
    
        else:
            return ""

# def fill_from_config(self, xomconfig):
#     analysis_version = xomconfig.get(self.analysis_name,'analysis_version')
#     containerlist = xomconfig.get(self.analysis_name,'container')
#     self.container_list = containerlist.split(',')

#         if xomconfig.has_option(self.analysis_name,'include_tags'):
#             include_tags_list  = xomconfig.get(self.analysis_name,'include_tags')
#             self.include_tags_list = include_tags_list.split(',')

#         if xomconfig.has_option(self.analysis_name,'available_type'):
#             available_type_list  = xomconfig.get(self.analysis_name,'available_type')
#             self.available_type_list = available_type_list.split(',')

#         variablelist = xomconfig.get(self.analysis_name,'variable_name')
#         self.variable_list = variablelist.split(',')
#         self.runwise = xomconfig.getboolean(self.analysis_name,'runwise')
#         self.folder = xomconfig.get(self.analysis_name,'folder')
#         self.command = xomconfig.get(self.analysis_name,'command')
#         if xomconfig.has_option(self.analysis_name,'min_run'):
#             self.min_run = int(xomconfig.get(self.analysis_name,'min_run'))
#         if xomconfig.has_option(self.analysis_name,'max_run'):
#             self.max_run = int(xomconfig.get(self.analysis_name,'max_run'))

#     def print_config(self):
#         print(f"##### Analysis: {self.analysis_name} version {self.analysis_version} ##########")
#         print("variable list =", self.variable_list)
#         print("container list =", self.container_list)
#         print("exclude_tags list =", self.exclude_tags_list)
#         print("include_tags list =", self.include_tags_list)
#         print("runwise = ", self.runwise)
#         print("command =", self.command)
#         print("###################################################")

#     xomconfig = get_xom_config(constant.configname)
#     logger.info('set up config with file %s: ', constant.configname)
#     analysis_names = xomconfig.sections()
    
#     ##############################################
#     ### filling a list with analysis instances ###
#     ##############################################
#     analysis_list = []
#     for analysis_name in analysis_names:
