import creds
import boto3
import face_recognition
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import numpy as np

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.FaceRecognitionAttendance
users = db["Users"]

s3_client = boto3.client(
    's3',
    region_name = creds.AWS_REGION_NAME,
    aws_access_key_id = creds.AWS_ACCESS_KEY_ID,
    aws_secret_access_key = creds.AWS_SECRET_ACCESS_KEY
)

#s3_client.download_file('zomz-test','0.jpeg','/home/soundarzozm/s3/0.jpeg')

#Helper Functions
def UserExists(username):
    if users.find({"username": username}).count() == 0:
        return False
    return True

def VerifyPassword(username, password):
    if not UserExists(username):
        return CreateJson(301, "username not found"), True

    hashed_pw = users.find({
        "username": username
    })[0]["password"]

    if bcrypt.checkpw(password.encode("utf8"), hashed_pw) != True:
        return CreateJson(302, "wrong password"), True
    else:
        return {}, False

def CreateJson(status, msg):
    retJson = {
        "status": status,
        "msg": msg
    }
    return jsonify(retJson)






if __name__ == "__main__":
    app.run(host="0.0.0.0") 