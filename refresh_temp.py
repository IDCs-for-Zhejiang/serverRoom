import schedule
import time
import datetime
#from random import randint
import pymongo
from pymongo import MongoClient #working with PyMongo



def job():
    # to update the actual power load of the server
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    answer = 0
    cursor = db.server.find()
    for record in cursor:
        if record["on"] == str(1):
            answer += 1
    cursor = db.actualTemperature.find().sort("time",-1).limit(answer)
    for record in cursor:
        db.server.update(
            { "Numbering": str(record["serverNumbering"]) },
            { "$set":
                {
                "actualTemperature": str(record["actualTemperature"])
                }
            }
        )

    # to check whether the actual power load exceed the threshold
    cursor = db.server.find()
    for record in cursor:
        if record["on"] == str(1):
            if int(record["actualTemperature"]) < int(record["thresholdTemperature"]):
                print("success")
            else:
                print("fail")
        else:
            print("false")

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
