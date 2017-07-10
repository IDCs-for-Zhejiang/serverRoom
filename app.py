from flask import Flask, jsonify
from flask import request #request the object
from flask import render_template #use this to render the template file
import json # to receive the data and transfer the data into the format that we need
import pymongo
import copy # for copy operation
import time
import csv
from pymongo import MongoClient #working with PyMongo
from bson.objectid import ObjectId
app = Flask(__name__)

#to show the insert webpage
@app.route('/insertpage')
def renderinsert():
    return render_template('insert.html')

@app.route('/searchpage')
def rendersearch():
    return render_template('search.html')

#insert the information of the candidate server to the collection server
@app.route('/searchaaa', methods=['POST'])
def insertServer():
    serverNumbering = request.form["Numbering"] #to get the data from the front end
    cabinetNumbering = request.form["cabinet numbering"]
    height = request.form["height"]
    category = request.form["category"]
    responsible = request.form["responsible"]
    ratedPower = request.form["rated power"]
    actualPowerLoad = request.form["actual power load"]
    actualTemperature = request.form["actual temperature"]
    thresholdTemperature = request.form["actual temperature"]
    startPosition = str(0)
    endPosition = str(0)
    onCabinet = str(0) #initially set all the server does not on the cabinet
    on = str(0) #initially set all the server off

    mydata = {} #transfer the data into the json format
    mydata["Numbering"] = str(serverNumbering)
    mydata["cabinetNumbering"] = str(cabinetNumbering)
    mydata["startPosition"] = str(startPosition)
    mydata["endPosition"] = str(endPosition)
    mydata["height"] = str(height)
    mydata["category"] = str(category)
    mydata["responsible"] = str(responsible)
    mydata["ratedPower"] = str(ratedPower)
    mydata["actualPowerLoad"] = str(actualPowerLoad)
    mydata["actualTemperature"] = str(actualTemperature)
    mydata["thresholdTemperature"] = str(thresholdTemperature)
    mydata["onCabinet"] = str(onCabinet)
    mydata["on"] = str(on)

    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    collection = db.server #getting a collection(table)
    collection.insert_one(mydata) #to insert the data into the database
    return 'success'

# find possible place where this server can be put in
@app.route('/searchccc', methods=['POST'])
def find_position():
    serverNumbering = request.form["serverNumbering"] #to get the data from the front end
    #serverNumbering = 128
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    # to put the server on the cabinet
    candidatePlace = {}
    serverNumbering = str(serverNumbering) # to get the maximum power and height of this special server
    maximumPower = db.server.find({"Numbering":serverNumbering},{"ratedPower":1,"_id":0})
    maximumHeight = db.server.find({"Numbering":serverNumbering},{"height":1,"_id":0})
    for record in maximumPower:
        power = int(record['ratedPower'])
    for record in maximumHeight:
        height = int(record['height'])
    cursor = db.Cabinet.find() # to find a appropriate position for this server
    for record in cursor:
        print("happy")
        cabinetNumbering = record["Numbering"]
        cabinetUnumber = record["uNumber"]# to get the number of units in this cabinet
        cabinetActualPower = record["actualTotalPowerLoad"]
        cabinetThresholdPower = record["thresholdPowerLoad"]
        # to get the current usage of the space
        initial_value = 0
        list_length = int(cabinetUnumber)
        current_usage = [ initial_value for i in range(list_length)]
        # Possible Choices
        possible_choises = [ initial_value for i in range(list_length)]
            #for element in sample_list:
                #print(element)

            #find_position = False
            #print(cabinetNumbering)
        cursor = db.server.find()
        for record in cursor:
            if record["cabinetNumbering"] == cabinetNumbering :
                start = int(record["startPosition"])
                end = int(record["endPosition"])
                pos = start - 1
                while pos < end:
                    current_usage[pos] = 1
                    pos += 1
            # continues space
        available_space_continues = False

            # last unavailable position
        last_unavailable_pos = 0

        for i, x in enumerate(current_usage):
            if x == 0:
                    # available space
                possible_choises[i] += 1
                if available_space_continues:
                    for j in range(last_unavailable_pos+1, i):
                            # print j, i
                        possible_choises[j] += 1

                else:
                    available_space_continues = True
                        # available_space_continues = True
            else:
                last_unavailable_pos = i
                available_space_continues = False

            #print possible_choises
        i = 0
        #print(cabinetNumbering)
        #print(power)
        #print(cabinetActualPower)
        #print(cabinetThresholdPower)
        find_position = False
        while i < len(possible_choises):
            if height > possible_choises[i] or (power+cabinetActualPower) > cabinetThresholdPower:
                i += 1
                continue
            else:
                startPos = i+1
                endPos = i+height
                candidatePlace[str(cabinetNumbering)] = {
                    "startPosition" : str(startPos),
                    "endPosition" : str(endPos)
                }
                break
    jsonStr = json.dumps(candidatePlace)
    return jsonStr

# to get the threshold value
@app.route('/searchbb', methods=['POST'])
def setData():
    cabinetNumbering = request.form["cabinetNumering"] #to get the data from the front end
    thresholdPower = request.form["thresholdPower"]
    num = str(cabinetNumbering)
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    db.Cabinet.update(
        { "Numbering": num },
        { "$set":
            {
            "thresholdPowerLoad": thresholdPower
            }
        }
    )
    return("success")

#return all the documents of the servers
@app.route('/search22', methods=['POST'])
def searchServer():
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    collection = db.server #getting a collection(table)
    cursor=collection.find()
    resultlist={}
    for record in cursor:
        serverNumber = int(record["Numbering"])
        resultlist[str(serverNumber)] ={
            "cabinetNumbering": record["cabinetNumbering"],
            "startPosition": record["startPosition"],
            "endPosition": record["endPosition"],
            "height": record["height"],
            "category": record["category"],
            "responsible": record["responsible"],
            "ratedPower": record["ratedPower"],
            "actualPowerLoad": record["actualPowerLoad"],
            "actualTemperature": record["actualTemperature"],
            "thresholdTemperature": record["thresholdTemperature"],
            "category": record["category"],
            "onCabinet" : record["onCabinet"],
            "on" : record["on"]
        }

    jsonStr = json.dumps(resultlist)
    return jsonStr

#return all the documents of the cabinets
@app.route('/searchdd', methods=['POST'])
def searchCabinet():
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    collection = db.Cabinet #getting a collection(table)
    cursor=collection.find()
    resultlist={}
    for record in cursor:
        cabinetNumber = int(record["Numbering"])
        resultlist[str(cabinetNumber)] ={
            "serverRoomTitle" : str(record["serverRoomTitle"]),
            "responsible" : str(record["responsible"]),
            "category" : str(record["category"]),
            "startDate" : str(record["startDate"]),
            "cabinetSize" : str(record["cabinetSize"]),
            "NumberingPowerCabinet" : str(record["NumberingPowerCabinet"]),
            "actualTotalPowerLoad" : str(record["actualTotalPowerLoad"]),
            "thresholdPowerLoad" : str(record["thresholdPowerLoad"]),
            "actualTemperature" : str(record["actualTemperature"]),
            "thresholdCoolingLoad" : str(record["thresholdCoolingLoad"]),
            "uNumber" : str(record["uNumber"])
        }
    jsonStr = json.dumps(resultlist)
    return jsonStr




# enter the number of the server to set the server on the cabinet
# and also need check whether this server can be set on the cabinet
@app.route('/searchmm', methods=['POST'])
def serverOnCabinet():
    serverNumbering = request.form["serverNumbering"] #to get the data from the front end
    #to do the right thing(1-put the server on the cabinet; 2-fetch the server from the cabinet; 3-turn the server on; 4-turn the server off)
    serviceNumber = request.form["serviceNumber"]
    cabinetNumber = request.form["cabinetNumber"]
    startPosition = request.form["startPosition"]
    endPosition = request.form["endPosition"]
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    # to put the server on the cabinet
    if int(serviceNumber) == 1:
        #cabinetNumbering = str(cabinetNumber)
        serverNumbering = str(serverNumbering) # to get the maximum power and temperature of this special server
        db.server.update( # to update the server state whether its on the cabinet
            { "Numbering": serverNumbering },
            { "$set":
                {
                "cabinetNumbering":str(cabinetNumber),
                "startPosition": str(startPosition),
                "endPosition": str(endPosition),
                "onCabinet": str(1)
                }
            }
        )
        return("success")

    # to fetch the server from the cabinet
    elif int(serviceNumber) == 2:
        serverNumbering = str(serverNumbering)
        db.server.update( # to update the server state whether its on the cabinet
            { "Numbering": serverNumbering },
            { "$set":
                {
                "actualPowerLoad":str(0),
                "actualTemperature":str(0),
                "cabinetNumbering":str(-1),
                "startPosition": str(0),
                "endPosition": str(0),
                "onCabinet": str(0),
                "on": str(0)
                }
            }
        )
        #db.server.delete_one({'Numbering': serverNumbering})
        #db.U.delete_one({'ServerNumbering': serverNumbering})
        return("success")
    # turn the server on
    elif int(serviceNumber) == 3:
        serverNumbering = str(serverNumbering)
        maximumPower = db.server.find({"Numbering":serverNumbering},{"ratedPower":1,"_id":0}) # to find the ratedPower for this particular server
        for record in maximumPower:
            power = int(record['ratedPower'])
        cabinetNumber = db.server.find({"Numbering":serverNumbering},{"cabinetNumbering":1,"_id":0}) # to find the cabinet of this server
        for record in cabinetNumber:
            CabinetNumber = record['cabinetNumbering']
        print(CabinetNumber)
        cabinetActualPower = db.Cabinet.find({"Numbering":CabinetNumber},{"actualTotalPowerLoad":1,"_id":0}) # to find the actual power and threshold power of this cabinet
        for record in cabinetActualPower:
            ActualPower = record['actualTotalPowerLoad']
        cabinetThresholdPower = db.Cabinet.find({"Numbering":CabinetNumber},{"thresholdPowerLoad":1,"_id":0})
        for record in cabinetThresholdPower:
            ThresholdPower = record['thresholdPowerLoad']
        powercabinet = db.Cabinet.find({"Numbering":CabinetNumber},{"NumberingPowerCabinet":1,"_id":0}) # to find the actual power and threshold power of this cabinet
        for record in powercabinet:
            powerCabinetNumber = record['NumberingPowerCabinet']
        powerCabinetThresholdPower = db.powerCabinet.find({"Numbering":powerCabinetNumber},{"thresholdPowerLoad":1,"_id":0})
        for record in powerCabinetThresholdPower:
            CabinetThresholdPower = record['thresholdPowerLoad']
        powerCabinetActualPower = db.powerCabinet.find({"Numbering":powerCabinetNumber},{"actualTotalPowerLoad":1,"_id":0})
        for record in powerCabinetActualPower:
            CabinetActualPower = record['actualTotalPowerLoad']
        if (power+ActualPower) > ThresholdPower or (power+CabinetActualPower) > CabinetThresholdPower:
            return("false")
        else:
            db.server.update( # to update the server state whether its on the cabinet
                { "Numbering": serverNumbering },
                { "$set":
                    {
                    "on": str(1)
                    }
                }
            )
            return("success")
    # turn the server off
    else:
        serverNumbering = str(serverNumbering)
        db.server.update(
            { "Numbering": serverNumbering },
            { "$set":
                {
                "actualPowerLoad":str(0),
                "actualTemperature":str(0),
                "on": str(0)
                }
            }
        )
        return("success")

# to delete the particular server
@app.route('/searchzz', methods=['POST'])
def deleteServer():
    serverNumbering = request.form["serverNumering"] #to get the data from the front end
    num = str(serverNumbering)
    #num = str(128)
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    db.server.delete_one({'Numbering': num})
    return("success")

#return all the documents of the cabinets
@app.route('/search', methods=['POST'])
def cabinetPower():
    client = MongoClient() #making a connection with MongoClient
    db = client.IDCs #getting a database of MongoDB
    collection = db.Cabinet #getting a collection(table)
    cursor=collection.find()
    resultlist={}
    for record in cursor:
        cabinetNumber = int(record["Numbering"])
        resultlist[str(cabinetNumber)] ={
            "cabinetNumber":str(cabinetNumber),
            "thresholdPowerLoad" : str(record["thresholdPowerLoad"])
        }
    jsonStr = json.dumps(resultlist)
    return jsonStr

if __name__ == '__main__':
    app.run(debug=True)
