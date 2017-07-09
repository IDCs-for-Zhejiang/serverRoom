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
    cursor = db.actualPower.find().sort("time",-1).limit(answer)
    for record in cursor:
        db.server.update(
            { "Numbering": str(record["serverNumbering"]) },
            { "$set":
                {
                "actualPowerLoad": str(record["actualPowerLoad"])
                }
            }
        )
    # to update the actual power load of the cabinet
    cursor = db.Cabinet.find()
    resultlist=[]
    answer=0
    for record in cursor:
        cursor = db.server.find()
        severlist = []
        cabinetNumber = record["Numbering"]
        for record in cursor:
            if record["cabinetNumbering"] == cabinetNumber and record["on"] == str(1):
                answer+=int(record["actualPowerLoad"])
    #print(answer)
    #print (str(collection.find_one({"Numbering": cabinetNumber})))
    #print(cabinetNumber)
        db.Cabinet.update(
            { "Numbering": cabinetNumber },
            { "$set":
                {
                "actualTotalPowerLoad": answer
                }
            }
        )
        answer = 0
    # to check whether the actual power load exceed the threshold
    cursor = db.Cabinet.find()
    resultlist=[]
    for record in cursor:
        if int(record["actualTotalPowerLoad"]) < int(record["thresholdPowerLoad"]):
            print("success")
        else:
            print("false")
    # to update the actual power load of the power cabinet
    cursor = db.powerCabinet.find()
    resultlist=[]
    answer=0
    for record in cursor:
        cursor = db.Cabinet.find()
        severlist = []
        powerCabinetNumber = record["Numbering"]
        for record in cursor:
            if record["NumberingPowerCabinet"] == powerCabinetNumber:
                answer+=int(record["actualTotalPowerLoad"])
    #print(answer)
    #print (str(collection.find_one({"Numbering": cabinetNumber})))
    #print(cabinetNumber)
        db.powerCabinet.update(
            { "Numbering": powerCabinetNumber },
            { "$set":
                {
                "actualTotalPowerLoad": answer
                }
            }
        )
        answer = 0
    # to check whether the actual power load exceed the threshold
    cursor = db.powerCabinet.find()
    resultlist=[]
    for record in cursor:
        if int(record["actualTotalPowerLoad"]) < int(record["thresholdPowerLoad"]):
            print("success")
        else:
            print("false")
    #print("success")
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
