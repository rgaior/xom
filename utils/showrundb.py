import pymongo
from pymongo import MongoClient
from utilix.rundb import pymongo_collection
from  utilix.config import Config
import pprint
rundb = pymongo_collection('runs')
excl = ["messy","abandon"]
excl_q = [{"tags.name":{"$ne": e}} for e in excl]
print(excl_q)

# query_excluded =  [ {"tags.name": "messy"} ,
#                     {"tags.name": "abandon"} ] 
                
# include_tags = [{"$regex":"_sr0"},"lt_24h_after_kr"]
# include_tags_query =  [{"tags.name": i} for i in include_tags]
# print(include_tags_query)
# #pprint.pprint(rundb.find_one({"$and" : query_excluded, "number":12258}))
# pprint.pprint(rundb.find_one({"$or" : include_tags_query}))
# #pprint.pprint(rundb.find_one({"tags.name":{"$regex":"_sr0"}}) )


exclude_tags = ["messy","bad", "nonsr0_configuration", "ramp down",  "ramp up",  "ramp_down", "ramp_up", "hot_spot","abandon"]
exclude_tags_query =  [{"tags.name":{"$ne": e}} for e in exclude_tags]

include_tags = [{"$regex":"_sr0"},"lt_24h_after_kr"]
include_tags_query =  [{"tags.name": i} for i in include_tags]

run_mode ='tpc_kr83m'
coll = list(rundb.find({"$and" : exclude_tags_query,"$or": include_tags_query, "mode":'tpc_kr83m'}))
#coll = list(rundb.find({"$and" : exclude_tags_query}))

print(coll)