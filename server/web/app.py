import face_recognition
import creds
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
from datetime import date
import os

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.FaceRecognitionAttendance
users = db["Users"]

#Helper Functions
def userExists(username):
    if users.find({"username": username}).count() == 0:
        return False
    return True

def createJson(status, msg):
    retJson = {
        "status": status,
        "msg": msg
    }
    return jsonify(retJson)

def updateAttendance(username):
    today_date = str(date.today())
    last_seen = users.find({
        "username": username
    })[0]["last_seen"]
    attendance = users.find({
        "username": username
    })[0]["attendance"]
    if today_date != last_seen:
        users.update({
                "username": username
            }, {
                "$set": {
                    "last_seen": today_date,
                    "attendance": attendance + 1
                }
            })
    return None

def compareFace(username):
    pic_db = face_recognition.load_image_file(username + ".jpg")
    pic_cam = face_recognition.load_image_file("test.jpg")
    face_encoding_db = face_recognition.face_encodings(pic_db)[0]
    face_encoding_cam = face_recognition.face_encodings(pic_cam)[0]
    return face_recognition.compare_faces([face_encoding_db], face_encoding_cam)[0]

def verifyAdmin(ADMIN, ADMIN_PW):
    if (userExists(ADMIN)==False) or (users.find({"admin":True, "username":ADMIN}).count() == 0):
        return createJson(304, "wrong admin"), True
    hashed_pw = users.find({
        "admin": True,
        "username": ADMIN
    })[0]["password"]
    if bcrypt.checkpw(ADMIN_PW.encode("utf8"), hashed_pw) != True:
        return createJson(303, "wrong password"), True
    else:
        return {}, False

def registerUpdate(username, password, admin, url=None):
    if userExists(username):
        return createJson(305, "user already registered")
    hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
    if admin==True:
        users.insert({
        "username": username,
        "password": hashed_pw,
        "admin": True
    })
    else:
        users.insert({
        "username": username,
        "password": hashed_pw,
        "admin": False,
        "last_seen": str(date.today()),
        "attendance": 1,
        "url": url
    })
    return createJson(200, "user created")

#End-points
class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        ADMIN = postedData["admin"]
        ADMIN_PW = postedData["admin_pw"]
        url = postedData["url"]

        retJson, error = verifyAdmin(ADMIN, ADMIN_PW)
        if error:
            return retJson

        retJson = registerUpdate(username, password, False, url)

        return retJson

class RegisterAdmin(Resource):
    def post(self):
        postedData = request.get_json()
        ADMIN = postedData["admin"]
        ADMIN_PW = postedData["admin_pw"]
        retJson = registerUpdate(ADMIN, ADMIN_PW, True)
        return retJson

class Check(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        url = postedData["url"]
        if userExists(username)==False:
            return createJson(302, "user not found")
        test_request = requests.get(url)
        user_request = requests.get(creds.S3_URL + username + ".jpg")
        with open("test.jpg", "wb") as f:
            f.write(test_request.content)
        with open(username + ".jpg", "wb") as f:
            f.write(user_request.content)
        result = compareFace(username)
        os.remove("test.jpg")
        os.remove(username + ".jpg")
        if result:
            updateAttendance(username)
            return createJson(200, "face matched")
        else:
            return createJson(301, "face mismatch")

api.add_resource(Register, "/register")
api.add_resource(RegisterAdmin, "/registeradmin")
api.add_resource(Check, "/check")

if __name__ == "__main__":
    app.run(host="0.0.0.0") 

#200 - OK
#301 - face mismatch
#302 - user not found
#303 - wrong password
#304 - wrong admin
#305 - user already registered