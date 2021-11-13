from flask import Flask, render_template, Response, request
import requests
import creds
import cv2
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # use 0 for web camera
# for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def upload_to_aws(local_file, bucket, s3_file):
    
    s3 = boto3.client('s3', aws_access_key_id = creds.ACCESS_KEY, aws_secret_access_key = creds.SECRET)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True

    except FileNotFoundError:
        print("The file was not found")
        return False

    except NoCredentialsError:
        print("Credentials not available")
        return False

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    img = camera.read()[1]
    username = request.form['username']
    cv2.imwrite('test.jpg', img)
    uploaded = upload_to_aws('test.jpg', 'itr-soundar', 'test.jpg')
    # url = "https://itr-soundar.s3.ap-south-1.amazonaws.com/test.jpg"
    # r = requests.post('http://172.19.0.3:5000/check', json={
    #     'username':username,
    #     'url': url
    # })

    

    return("None")

if __name__ == '__main__':
    app.run(debug=False)
