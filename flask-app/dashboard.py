#!/usr/bin/env python
from __future__ import division
import flask
from flask import request, render_template, jsonify
import boto3
from boto3.dynamodb.conditions import Key, Attr
import pickle
import datetime
import time
import json
import sys

# Create the application.
APP = flask.Flask(__name__)

#Enter AWS Credentials
AWS_ACCESS_KEY="AKIAJZQGVFSZNTUQQEDA" 
AWS_SECRET_KEY=""
REGION="us-east-2"

# Get the table
dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY,
                            region_name=REGION)

table = dynamodb.Table('SensorData')

@APP.route('/data')
def get_Data():
    try:
        data = {}
        ts=time.time()
        
        timestampold = datetime.datetime.fromtimestamp(ts-60).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        response = table.scan(
            FilterExpression=Key('Timestamp').between(timestampold, timestamp)
        )
        items = response['Items']

        if len(items) > 0:
            data["co2"] = int(items[0]["CO2"])
            data["temperature"] = int(items[0]["Temperature"])
            data["light"] = int(items[0]["Light"])
            data["humidity"] = int(items[0]["Humidity"])
            return jsonify(data)

        else:
            return jsonify({'temperature': 0, 'humidity': 0,'co2': 0,'light': 0})

    except Exception as err:
        print("Unexpected error:", err)
        pass
            
    return jsonify({'temperature': 0, 'humidity': 0,'co2': 0,'light': 0})

@APP.route('/updateData')
def update_data():
    try:
        data = {}
        ts=time.time()
        
        timestampold = datetime.datetime.fromtimestamp(ts-60).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        response = table.scan(
            FilterExpression=Key('Timestamp').between(timestampold, timestamp)
        )
        items = response['Items']

        co2Vals = []
        tempVals = []
        lightVals = []
        humVals = []
        if len(items) > 0:
            for item in items:
                co2Vals.append(item["CO2"])
                tempVals.append(item["Temperature"])
                lightVals.append(item["Light"])
                humVals.append(item["Humidity"])

            co2Max = max(co2Vals)
            co2Min = min(co2Vals)
            co2Mean = sum(co2Vals)/len(co2Vals)

            tempMax = max(tempVals)
            tempMin = min(tempVals)
            tempMean = sum(tempVals)/len(tempVals)

            lightMax = max(lightVals)
            lightMin = min(lightVals)
            lightMean = sum(lightVals)/len(lightVals)

            humMax = max(humVals)
            humMin = min(humVals)
            humMean = sum(humVals)/len(humVals) 

            data["co2Max"] = int(co2Max)
            data["co2Min"] = int(co2Min)
            data["co2Mean"] = int(co2Mean)

            data["tempMax"] = int(tempMax)
            data["tempMin"] = int(tempMin)
            data["tempMean"] = int(tempMean)

            data["lightMax"] = int(lightMax)
            data["lightMin"] = int(lightMin)
            data["lightMean"] = int(lightMean)

            data["humMax"] = int(humMax)
            data["humMin"] = int(humMin)
            data["humMean"] = int(humMean)
            return jsonify(data)

        else:
            return jsonify({'co2Max': 0, 'co2Min': 0,'co2Mean': 0,'tempMax': 0
                , 'tempMin': 0, 'tempMean': 0, 'lightMax': 0, 'lightMean': 0, 'humMax': 0,
                'humMin': 0, 'humMean': 0  })

    except Exception as err:
        print("Unexpected error:", err)
        pass
            
    return jsonify({'co2Max': 0, 'co2Min': 0,'co2Mean': 0,'tempMax': 0
                , 'tempMin': 0, 'tempMean': 0, 'lightMax': 0, 'lightMean': 0, 'humMax': 0,
                'humMin': 0, 'humMean': 0  })

@APP.route('/')
def index():
    return render_template('dashboard.html')

@APP.route('/getdata/<string:startDate>/<string:endDate>', methods=['GET'])
def filter_data(startDate, endDate):
    response = table.scan(
        FilterExpression=Key('Timestamp').between(startDate, endDate)
    )
    items = response['Items'];
    if len(items) > 0:
        itemList = [];
        for item in items:
            entry = {};
            entry["Timestamp"] = item["Timestamp"]
            entry["Temperature"] = item["Temperature"]
            entry["CO2"] = item["CO2"]           
            entry["Light"] = item["Light"]
            entry["Humidity"] = item["Humidity"]
            itemList.append(entry)

    return render_template('filterPage.html', itemList = itemList)

@APP.route('/getdata')
def filterPage():
    return render_template('filterPage.html')
if __name__ == '__main__':
    APP.debug=True
    APP.run(host='0.0.0.0', port=80)
