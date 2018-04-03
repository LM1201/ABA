
from pymongo import MongoClient

client = MongoClient()
i=0
num =len(client.database_names())
for name in  client.database_names():
    i+=1
    print name,i
    client.drop_database(name)
