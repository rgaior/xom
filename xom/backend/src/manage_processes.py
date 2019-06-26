import os
import json
import pprint
from datetime import datetime
import logging
import warnings

# import of the necessary classes
try:
    from electron_life_time import ElectronLifetime
    from light_yield import LightYield
    from charge_yield import ChargeYield
except Exception as err:
    print( "the error {}".format( err ) )

log = logging.getLogger( 'pm' )


class ProcessManager( object ):

    def __init__(self, dataframe=None, run_id=None, run_name=None, straxen_version=" ", data_stream=" ", source=" "):

        # here data stream: takes either calibration or background
        self.data_stream = data_stream
        # run_id: file run number
        self.run_id = run_id
        # run_name: file name
        self.run_name = run_name
        # straxen version, needed for the info dictionary that should contain all infos
        self.straxen_version = straxen_version
        # data source: if the data stream is calibration then
        self.source = source
        self.processes = {}
        self.info = {}
        # self.data_type = data_type
        self.source = source
        self.jsonFileName = str( self.run_id ) + ".json"
        self.df = dataframe
        # The krypton source has two lines and the summ, the energies are in keV
        if self.source == 'kr':
            self.energy_lines = [9, 32, 41]

    def get_file_time_info(self):
        """
        get the initial time and end time of a file
        """
        return {"start_time": int( self.df["time"].min() ), "end_time": int( self.df["time"].max() )}

    def fill_info(self):

        self.info.setdefault( 'info', {} ).update( {'filename': self.run_name} )
        self.info.setdefault( 'info', {} ).update( {'run': int( self.run_id )} )
        # if the length of the file is 0,  we won't be able to calculate the time of events
        if self.df:
            fileTimeInfo = self.get_file_time_info()
        else:
            fileTimeInfo = 0

        self.info.setdefault( 'info', {} ).update( fileTimeInfo )
        self.info.setdefault( 'info', {} ).update( {'offline production time': \
                                                        int( (datetime.now() - datetime( 1970, 1,
                                                                                         1 )).total_seconds() * 1.e9 )} )
        self.info.setdefault( 'info', {} ).update( {'user': os.getlogin()} )
        self.info.setdefault( 'info', {} ).update( {'original entries': \
                                                        len( self.df )} )
        self.info.setdefault( 'info', {} ).update( {'straxen version': \
                                                        self.straxen_version} )

        self.info.setdefault( 'info', {} ).update( {'type': \
                                                        self.data_stream} )
        if self.data_stream == "calibration":
            self.info.setdefault( 'info', {} ).update( {'source': \
                                                            self.source} )

    def write_json_file(self):
        """
        dump results into json file
        """
        # first start with the runid as an info
        # run fill_info to initiate the infos that needs to be dumped into the Json file
        self.fill_info()

        mergedDict = self.info.copy()

        if isinstance( self.processes, dict ):
            mergedDict.update( self.processes )
        pp = pprint.PrettyPrinter( indent=2 )
        print( "the json file: %s  is being writen " % self.jsonFileName )
        with open( self.jsonFileName, "w" ) as f:
            json.dump( mergedDict, f )
        pp.pprint( mergedDict )

    def process(self):
        """ Here comes the processes, EL, LY, CY"""
        pp = pprint.PrettyPrinter( indent=4 )

        if self.data_stream == 'calibration':
            print( "The electron life time:" )

            outputFileName = str( self.run_id ) + "_el_lifetime.png"
            # Initialize the electron life time class
            el_lifetime = ElectronLifetime( data=self.df, run_number=self.run_id, figname=outputFileName, source=self.source )
            # Get the electron life time
            result = el_lifetime.get_electron_lifetime()
            pp.pprint( result )
            if isinstance( result, dict ):
                self.processes.setdefault( 'processes', {} ).update( result )
            else:
                ##We need to add an empty json file not to crash the monitoring with stupid data.
                log.warning( "Failed to get the electron lifetime" )

            # Get the light yield
            # run for Light Yield and Charge yield for given energy lines from a given source
            if self.source == 'kr':
                for i, eline in enumerate( self.energy_lines ):
                    # calculate the light yield for only 9keV and 32keV and the charge yield for the sum i.e. 41keV
                    if i < 2:
                        print( "The light yield for Kr: %s keV line is ongoing" % eline )
                        outputFileName = str( self.run_id ) + '_%skev_light_yield.png' % eline

                        light_yield = LightYield( data=self.df, line="cs1", energy='%3.2f' % eline,
                                                  run_number=self.run_id, figname=outputFileName, source=self.source )
                        result = light_yield.get_light_yield()
                        pp.pprint( result )

                        if isinstance( result, dict ):
                            self.processes.setdefault( 'processes', {} ).update( result )
                        else:
                            ##We need to add an empty json file not to crash the monitoring with stupid data.
                            log.warning( "Failed to get the Light Yield for 32keV line" )
                    else:
                        # use the 41keV line to calculate the charge yield
                        print(
                            "the charge yield for Kr source is calculated for the sum of both gammas: %skeV" % eline )

                        outputFileName = str( self.run_id ) + "_%skeV_charge_yield.png" % eline
                        charge_yield = ChargeYield( data=self.df, line='s2_bottom', energy='%3.2f' % eline,
                                                    run_number=self.run_id, figname=outputFileName, source=self.source )

                        result = charge_yield.get_charge_yield()
                        pp.pprint( result )

                        if isinstance( result, dict ):
                            self.processes.setdefault( 'processes', {} ).update( result )

                        else:
                            log.warning( "Failed to get the Charge Yield line" )
