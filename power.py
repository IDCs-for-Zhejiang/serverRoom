import schedule
import time
import datetime
from random import randint
import pymongo
from pymongo import MongoClient #working with PyMongo

def job():
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    collection = db.actualPower #getting a collection(table)
    serverNumbering = 120
    datalist = []
    mydata = {} #transfer the data into the json format
    mydata["time"] = datetime.datetime.utcnow()
    while serverNumbering <= 127:
        mydata["serverNumbering"] = serverNumbering
        mydata["actualPowerLoad"] = randint(70,100)
        datalist.append(mydata.copy())
        serverNumbering +=1
    collection.insert(datalist) #to insert the data into the database
    print("success")

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
