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
- python proc_runner.py

One can check the latest entry in the data base in /utils/:
- python xomdblib.py --latest

