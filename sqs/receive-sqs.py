import boto3
import time
import json
import os
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

AWS_KEY="AKIAJZQGVFSZNTUQQEDA"
AWS_SECRET=""
REGION="us-east-2"
BUCKET = "aisayas3"
sqs = boto3.resource('sqs', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_KEY,
                                    aws_secret_access_key=AWS_SECRET,
                                    region_name=REGION)

# Get the queue
queue = sqs.get_queue_by_name(QueueName='SensorData')

# Get the table
table = dynamodb.Table('SensorData')

class myTimedRotatingHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='S', interval=10, backupCount=0, encoding=None, delay=False, utc=False):
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)
        print("STARTED")
        self.filename = filename
        self.start = time.time()


    def doRollover(self):
        if self.stream:
            self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)

        self.mode = 'w'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        fName = "logfile"
        s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,
                                    aws_secret_access_key=AWS_SECRET)

        filenameWithPath = self.filename + "." + datetime.datetime.fromtimestamp(self.start).strftime('%Y-%m-%d_%H-%M-%S')
        path_filename = fName + "." + datetime.datetime.fromtimestamp(self.start).strftime('%Y-%m-%d_%H-%M-%S')

        s3.upload_file(dfn, BUCKET, path_filename)

        s3.put_object_acl(ACL='public-read', Bucket=BUCKET, Key=path_filename)

        self.start = time.time()
        self.rolloverAt = newRolloverAt

log_filename='/tmp/log_rotate'
logger=logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)
handler = myTimedRotatingHandler(log_filename, interval=120)
logger.addHandler(handler)

def publish(data1):
    data = json.loads(data1)
    table.put_item(
       Item={
                "Timestamp": data['timestamp'],
                "Temperature": data['temperature'],
                "Humidity": data['humidity'],
                "Light": data['light'],
                "CO2": data['co2']
            }
        )

while True:
    for message in queue.receive_messages(MaxNumberOfMessages=1):
        print (message.body)
        data = message.body
        publish(data)
        logger.info(data)
        message.delete()
    time.sleep(2)
