import time
import os
import pickle
import pymongo

uri = "mongodb://rucio:%s@rundbcluster-shard-00-00-cfaei.gcp.mongodb.net:27017," \
      "rundbcluster-shard-00-01-cfaei.gcp.mongodb.net:27017," \
      "rundbcluster-shard-00-02-cfaei.gcp.mongodb.net:" \
      "27017/test?ssl=true&replicaSet=RunDBCluster-shard-0&authSource=admin&retryWrites=true"
client = pymongo.MongoClient( uri % os.environ.get('RUCIO_PASSWORD') )
db = client['test']

# create the xom collection

try:
    mycollection = db['xom_test']
except Exception as err:
    print( "the error: ", err )

for fname in os.listdir( os.getcwd() ):
    if fname.endswith( ".pck" ):
        print("we found one pickle file:%s"%fname )
        try:
            mydocument = pickle.load( open( fname, "rb" ) )
            result = mycollection.insert_one( mydocument )
            print( 'Created {0} as {1}'.format( fname, result.inserted_id ) )
            print( "we sleep for a minute ..." )
            time.sleep( 30 )

        except Exception as err:
            print( "the document could not be loaded from the pickle file", err )

print( "finished creating 4 kr objects" )
