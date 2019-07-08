import os
import sys
from glob import glob
from json2mongo import WriteToDataBase



filename = "last_run_context_numbers.txt"
# argument to be provided to the process manager
parser = argparse.ArgumentParser( description="process manager" )
# need this to read the ini file
config = configparser.ConfigParser()
config.read( "pm.ini" )

parser.add_argument( '--mainDir',
                     default=config["LNGS"]["maindirectory"],
                     type=str,
                     help="Name of the main directory at LNGS for data" )
parser.add_argument( '--DBLngs',
                     default=config["LNGS"]["db_lngs"],
                     type=str,
                     help="Name of the data base at LNGS" )



# Get the object of arguments, args
args = parser.parse_args()

def read_run_context():
    """
    read the file last_run_context_numbers.txt and give back the the run & context numbers
    """
    global filename
    # read the last_run.txt file and get the last run and the context_version
    file_infos  = open(filename, "r")
    last_run = int(file_infos.readline())
    last_context_version = file_infos.readline()
    return last_run, last_context_version

def loop_over_main_dir(main_dir = None, databse=None):
    """
    Loop over the directory $HOME/data/xom and get the main directories
    The idea is to compare the context versions then the run numbers
    """
    last_run, last_context = read_run_context()
    list_contexts = []
    for name in os.listdir( main_dir ):
        if os.path.isdir( main_dir + name ):
            list_contexts.append( name )

    if len(list_contexts) > 1:
        for newcontext  in list_contexts:
            # we are going to loop over the new context and write what is inside it to the DB
            if newcontext > last_context :
                # we go to the new directory that is made from the new context
                current_dir = main_dir + newcontext
                #lets go inside
                os.chdir(current_dir)
                # we need the run number inside this new context, of course there is only one
                jsonfilename = glob("*.json")[0]
                run_number = int(jsonfilename.rstrip(".json"))

                dbwriter = WriteToDataBase(datapath=current_dir, database=database,
                                           collection=newcontext, runnumber=run_number,
                                           jsonfile=jsonfilename)
                try:
                    # first we modify the path of the figures inside the json file
                    dbwriter.modify_jsonfile()

                    # now lets write the json file inside the data base
                    dbwriter.write_to_db()
                except Exception as err:
                    print("we can't write the json file to the data base")
                    print("the error: ", err)

    elif len(list_contexts) == 1:
        if list_contexts[0] == last_context :
            # we are still under the same versions of the context
            
            # we get into the directory of that context version and loop over directories
            old_context_directory = main_dir + last_context

            # each directory has a name which is the run number
            list_run_directories = []
            for name in os.listdir( old_context_directory ):
                if os.path.isdir( old_context_directory + name ):
                    list_run_directories.append( int( name ) )
            
            # now get the run_numbers and compare them to the old one
            for newrun in list_run_directories:
                if newrun - last_run == 0:
                    # there are no changes in the run numbers just quit here.
                    break
                # compare each run_directory with the old one:
                elif newrun - last_run >=1 :
                    current_dir = old_context_directory + name
                    # lets go inside
                    os.chdir( current_dir )
                    # we need the run number inside this new context, of course there is only one
                    jsonfilename = glob( "*.json" )[0]
                    run_number = int( jsonfilename.rstrip( ".json" ) )

                    dbwriter = WriteToDataBase( datapath=current_dir, database=database,
                                                collection=last_context, runnumber=run_number,
                                                jsonfile=jsonfilename )
                    try:
                        # first we modify the path of the figures inside the json file
                        dbwriter.modify_jsonfile()

                        # now lets write the json file inside the data base
                        dbwriter.write_to_db()
                    except Exception as err:
                        print( "we can't write the json file to the data base" )
                        print( "the error: ", err )

                    
    else:
        sys.exit("something is wrong with the module:%s" %"write_json_to_db.py")
