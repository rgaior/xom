#!/usr/bin/env python
import os
import sys
import pprint 
import numpy as np
import time
import constant
import info
import datetime
from dateutil.tz import tzutc
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatterch = logging.Formatter('%(name)-20s - %(levelname)-5s - %(message)s')
ch.setFormatter(formatterch)

########################
### connection to DB ###
########################


class Xomdb:
    def __init__(self, type_of_db, measurement_name):
        self.type_of_db= type_of_db
        self.client  = None
        self.measurement_name = measurement_name
        self.connect()
        self.logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)
        self.logger.debug(f"creating instance of {self.__class__}")
        # add the handlers to the logger
        self.logger.addHandler(ch)
    def connect(self):
        if self.type_of_db == 'influxdb':
            try:
                client = influxdb_client.InfluxDBClient(
                    url=info.url,
                    token=info.token,
                    org=info.org
                )   
            except:
                print('could not connect to the DB {} '.format(database) )
        self.client = client

    
    def get_last_runid(self):
        '''will query the latest runid'''
        if self.type_of_db == 'influxdb':
            query_api = self.client.query_api()
            fluxquery = 'from(bucket:"xom")  |> range(start: '+ str(-constant.query_period) + 'd) |> filter(fn: (r) => r._measurement == \"' +self.measurement_name + '\")|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |>group()|> max(column:"runid")'
            try:
                tables = query_api.query(fluxquery)
                self.last_run_id = tables[0].records[0]['runid']
            except:
                self.last_run_id = -1
        return self.last_run_id

    def get_last_runid_from_analysis(self, analysis_name):
        '''will query the latest runid'''
        if self.type_of_db == 'influxdb':
            query_api = self.client.query_api()
            fluxquery = 'from(bucket:"xom")  |> range(start: '+ str(-constant.query_period) + 'd) |> filter(fn: (r) => r._measurement ==  \"' + self.measurement_name + '\") |> filter(fn: (r) => r.analysis_name == \"'+ analysis_name + '\")|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> max(column:"runid")'
            try:
                tables = query_api.query(fluxquery)
                last_run_id = tables[0].records[0]['runid']
            except:
                last_run_id = -1
            return last_run_id

            

    def insert_record(self, record):
        '''
        record or list of record
        '''
        write_api = self.client.write_api(write_options=SYNCHRONOUS)    
        if isinstance(record,list):
            for r in record:
                write_api.write(bucket="xom", org=self.client.org, record=r)
        else:
            write_api.write(bucket="xom", org=self.client.org, record=record)
 
    def insert(self, result):
        '''related to the data format from the xomsaver in xomlib 
        result['analyse_name'] = analysis_name
        result['timestamp'] = int(timestamp/1e9)
        result['run_id'] = int(run_id)
        result['var_name'] = var_name
        result['container'] = container
        result['value'] = var_value
        result['type'] = type
        result['tag'] = tag
        result['data'] = data
        '''
        if self.type_of_db == 'influxdb':
            write_api = self.client.write_api(write_options=SYNCHRONOUS)    
#            p = influxdb_client.Point(self.measurement_name).field(result['var_name'], result['value']).tag("type", "main").tag("analyse", result['analysis_name']).tag("container",result['container']).field("runid", result['runid'])

            p = influxdb_client.Point(self.measurement_name).field('var_name',result['var_name']).field("analysis",result['analysis_name']).field('output', result['value']).tag("type", result['type']).tag("container",result['container']).field("runid", result['runid'])
            write_api.write(bucket="xom", org=self.client.org, record=p)
            if result['data']:
                outdata = []
                for datum in data:
                    p = influxdb_client.Point(constant.xomversion).field(result['var_name'], result['value']).tag("type", "extra").tag("analyse", result['analysis_name']).tag("container",result['container'].field("runid", result['runid']))
                    outdata.append(p)
                write_api.write(bucket="xom", org=self.client.org, record=outdata)
        elif self.type_of_db == 'mongodb':
            xomdata = self.client['xom']['data']
            xomdata.insert_one(result)


    def insert_first(self, var_name):
        if self.type_of_db == 'influxdb':
            write_api = self.client.write_api(write_options=SYNCHRONOUS)    
            p = influxdb_client.Point(constant.xomversion).tag("runid", str(result['runid'])).field(result['var_name'], result['value']).tag("type", "main").tag("analyse", result['analysis_name']).tag("container",result['container'])
            write_api.write(bucket=bucket, org=org, record=p)
            if data:
                for datum in data:
                    p = influxdb_client.Point(constant.xomversion).tag("runid", str(result['run_id'])).field(result['var_name'], datum).tag("type", "extra").tag("analyse", result['analysis_name']).tag("container",result['container'])
                    write_api.write(bucket=bucket, org=org, record=p)
        elif self.type_of_db == 'mongodb':
            xomdata = self.client['xom']['data']
            xomdata.insert_one(result)

    def query_all(self):
        query_api = self.client.query_api()
        fluxquery = 'from(bucket:"xom")|> range(start: '+ str(-constant.query_period) + 'd) |> filter(fn: (r) => r._measurement ==  \"' + self.measurement_name + '\") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |>group() '
        tables = query_api.query(fluxquery)
        return tables

    def query(self, query):
        query_api = self.client.query_api()
        fluxquery = query
        #'from(bucket:"xom")  |> range(start: '+ str(-constant.query_period) + 'd) |> filter(fn: (r) => r._measurement ==  \"' + self.measurement_name + '\") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |>group() '
        tables = query_api.query(query)
        return tables

    def get_list(self):
        query_api = self.client.query_api()
        fluxquery = 'from(bucket:"xom")  |> range(start: '+ str(-constant.query_period) + 'd) |> filter(fn: (r) => r._measurement ==  \"' + self.measurement_name + '\") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> group() '
        tables = query_api.query(fluxquery)
        return tables
        

    def get_dict_from_record(self,p):
        return {"var_name":p['var_name'],'runid':p['runid'],'analysis_name':p['analysis_name'],"type": p['type'],'container':p['container'],'value':p['output'],'data':None}
        
#     def insert_p(self,p):
#         write_api = self.client.write_api(write_options=SYNCHRONOUS)
#         p = {'result': '_result', 'table': 0, '_start': datetime.datetime(2022, 12, 26, 22, 56, 20, 706467, tzinfo=tzutc()), '_stop': datetime.datetime(2023, 4, 5, 22, 56, 20, 706467, tzinfo=tzutc()), '_time': datetime.datetime(2023, 4, 5, 22, 48, 37, 959693, tzinfo=tzutc()), 'measurement': 'xomdone', 
# #        p = influxdb_client.Point(self.measurement_name).field('var_name',"toto").field("analysis","analystoto").field('output', 23).tag("type", "main").tag("container","conttoto").field("runid",12)    
#         print(p)
#         write_api.write(bucket="xom", org=self.client.org, record=p)

    def delete(self):
        start = "1970-01-01T00:00:00Z"
        stop = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        delete_api = self.client.delete_api()
        delete_api.delete(start, stop,'_measurement=\"' + self.measurement_name + '\"', bucket='xom')

    def delete_record(self, p):
        d1 = datetime.timedelta(microseconds=-1)
        d2 = datetime.timedelta(microseconds=+1)
        start = p['_time'] + d1
        stop = p['_time'] + d2
        delete_api = self.client.delete_api()
        delete_api.delete(start, stop,'_measurement=\"' + self.measurement_name + '\"', bucket='xom')

        



# def connect_to_XOM_DB(db = 'influxdb'):
#     if database = 'influxdb':
#         try:
#             client = influxdb_client.InfluxDBClient(
#                 url=info.url,
#                 token=info.token,
#                 org=info.org
#             )   
#         except:
#             print('could not connect to the DB {} '.format(database) )
#     elif database = 'mongodb':
#         try:
#             client = MongoClient(constant.server_address[server], 27017)
#         except:
#             print('could not connect to the DB from  {} with address {} '.format(server, constant.serveraddress[server]))
#     else:
#         print('wrong database name, should be in ', constant.database_list)
#     return client

# def connect_to_DB(database, server=None):
#     if database = 'influxdb':
#         try:
#             client = influxdb_client.InfluxDBClient(
#                 url=info.url,
#                 token=info.token,
#                 org=info.org
#             )   
#         except:
#             print('could not connect to the DB {} '.format(database) )
#     elif database = 'mongodb':
#         try:
#             client = MongoClient(constant.server_address[server], 27017)
#         except:
#             print('could not connect to the DB from  {} with address {} '.format(server, constant.serveraddress[server]))
#     else:
#         print('wrong database name, should be in ', constant.database_list)
#     return client
 


# def get_max_influxdb(client, name_of_variable, query=None):
# ''' by default will query the latest entry from the given name_of_variable, will apply the query if given in argument'''
#     query_api = client.query_api()
#     if query : 
#         fluxquery = query
#     else:
#         fluxquery = 'from(bucket:"xom") |>  range(start: '+ -constant.query_period+ 'd) |> filter(fn: (r) => r.variable_name =='+ variable_name + ') |> sort(columns: ["runid"] ) '
#         max = client.query_api(fluxquery)
#     return max

    # if there is an error when no query is given, try the following:
    #         max = col.find({}).sort(name_of_variable,-1).limit(1)[0][name_of_variable]



# # # influx db client

# # client = influxdb_client.InfluxDBClient(
# #    url=url,
# #    token=token,
# #    org=org
# # )


# # p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
# # write_api.write(bucket=bucket, org=org, record=p)




