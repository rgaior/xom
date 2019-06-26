#!/usr/bin/env python
import os
import sys
import datetime
import pymongo

def getKrCalibration(time_of_day='2019-01-01 00:00:00') :
    """
    it queries the RunDB for data that comes within one 4 hours
    """

    #This function interacts with the XENON1T runDB:
    #global run_number, pax_version
    #print("even before we start looking at files: %s" % time_of_day)

    uri = 'mongodb://pax:%s@copslx50.fysik.su.se:27017/run'
    uri = uri % os.environ.get('MONGO_PASSWORD')
    client = pymongo.MongoClient(uri, replicaSet='runs', readPreference='secondaryPreferred')

    db = client['run']
    collection = db['runs_new']
    
    #Create a query of the recent days (rc_days)
    # -for all Kr data for the last 360 days
    
    #dt_today = datetime.datetime.today()
    #dt_recent = timedelta(days=rc_days)
    #dt_begin = dt_today - dt_recent
    #for debug 
    #dt_begin  = datetime.datetime(2017, 6, 7, 11, 20, 4)
    dt_begin = datetime.datetime.strptime( time_of_day, '%Y-%m-%d %H:%M:%S' )
    dt_end = dt_begin + datetime.timedelta(days=0, hours=1, minutes=2, seconds=0)
    #dt_end    = datetime.datetime(2017, 9, 1, 0, 0)
    
    query =  {"source.type": "Kr83m", "start": {'$gt': dt_begin}, "end":{"$lt":dt_end}}#, "tags.name": "_sciencerun1"}#, "tags.name": "_sciencerun0"}

    cursor = list( collection.find(query) ) # make a list of the results of the querry

    #get the version of pax    

    #print('the type of that observable before we get it to querry is: ', type(cursor[0]))
    for i_c in cursor:
        #print('the type of this i_c: ', type(i_c))
        run_number = i_c['number']
        run_name  = i_c['name']
        #run_start = i_c['start']
        #run_end   = i_c['end']
        run_source = i_c['source']['type']
        #print("the type of source", run_source)
        if "data" in i_c.keys():
            pax_version = "pax_%s" % i_c["data"][0]["pax_version"]

        TagFile = False
        if 'tags' in i_c.keys() and len(i_c['tags']) > 0:            
            for itagdict in i_c['tags']:
                for v in itagdict.values():
                    if (isinstance(v,str)) and (v in ["bad","messy","_blinded"]): 
                        #print("this run must be bad: ", run_name, v)
                        TagFile = True
                        break

        if not TagFile:
            if run_source in ["Kr83m" , "Rn220"]:
                data_type = "calibration"
                run_source = "kr"
            else:
                data_type= "background"
                run_source = " "
            #run_dbtags.append((run_number, run_name, pax_version))
    print(data_type, run_source, run_name, run_number, pax_version)
    sys.exit(1)

if __name__ == "__main__":
    getKrCalibration(sys.argv[1])

