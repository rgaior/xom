XOM - Xenon Offline Monitoring
=

* Free software: BSD license
* Documentation: Available on internal XENON wiki

Features
--------

* Analyses XENONnT data and monitors useful quantities through a web application
* The web app is the xenon grafana

Usage
--------
the codes runs 
in screen session 1, enter the containre xenon.development.simg 
in screen session 2 load modules python and singularity:
- module load python
- module load singularity

choose the analysis to be computed in the /utils/xomconfig.cfg

Then in screen 1 go to /backend/ and execute:
- python proc_compare.py
In screen 2 go to /backend/ and execute:
in an environnement with influxdb-client and numpy isntall with pip
- python proc_runner.py

One can check the latest entry in the data base in /utils/:
- python xomdblib.py --latest




Influxdb structure: 
----------------------
measurement: xom version
field: variable
Tag1: analysis name
Tag2: variable name
Tag3: container
field: runid
Tag3: optional analyse dependant tag (example raw / mean)



Todo list:
------------------------ 
result object cleaner
cron tab instead of a while true
job out files handling
in dblib: declare once the query_api etc
test if data are available before putting the job in the todo db
handle the import of xomlib 
describre well the running procedure

write check functions
The way to delete the records is now by deleting +- 1us of the time of the record. Maybe cleaner way exist
The todo record show the other variable name, which is not foreseen...
Query of many runs in the DB
include detector in the selection of run (in analysis.py) and in the config file (could include non TPC analysis ?)
better check of the number of runs (with --name )
better check of the available datatype 
implement the check 

done list:
------------- 
--Job success check--
submitted database to store the entry while it is being run. 
If the run doesn't succeed, the entry will stay and not go to the done db
The job is considered successful if the analysis has reached the point where xom prints SUCCESSWITHXOM.
proc_runner checks that this message is in the output file.

-- 