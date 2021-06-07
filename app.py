# import library for backend connection
import os
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.utils import secure_filename

# importing the required libraries for spreadsheet
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# importing the required libraries for image
import os
import numpy as np
import cv2 as cv
from PIL import Image

# define required parameter 
app = Flask(__name__, template_folder="template",static_url_path='/static')
app.config["UPLOAD_FOLDER"] = "FACE-API/static"
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "common key"
sess = Session(app)

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('helper/face-recognition-cnn-dcf6c99e9e72.json', scope)
# authorize the clientsheet 
client = gspread.authorize(creds)
# get the instance of the Spreadsheet
sheet = client.open('Database Matriks Face ')
# get the instance of the second sheet
sheet_runs = sheet.get_worksheet(1)

# Load the cascade
face_cascade = cv.CascadeClassifier('helper/haarcascade_frontalface_alt2.xml')

@app.route("/", methods=["GET","POST"])
def main():
    if request.method == "POST":
        if request.files['image'].filename != '':
                image = request.files['image']
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(image.filename)))
                
                # request NIK & Convert Image to matrix then store to spreadsheet
                nik_value = request.form["nik"]
                # load image & preprocessing image
                image_original = np.array(Image.open(image))
                grayscaled = cv.cvtColor(image_original, cv.COLOR_BGR2GRAY)
                # detect face in image
                faces = face_cascade.detectMultiScale(grayscaled, 1.5, 1)
                # Draw rectangle around the faces and crop the faces
                for (x, y, w, h) in faces:
                    faces = grayscaled[y:y + h, x:x + w]
                # apply resize 300x300
                resized = cv.resize(faces, (300,300))
                # save resized & nik_value to spreadsheet
                sheet_runs.insert_row([nik_value])
                # belum save image (g-drive / local github)
                return redirect("/")
        else :
            return redirect("/")
    else:
        return render_template("index.html")
@app.route("/blank", methods=["GET"])
def blank():
    return render_template("main.html")

if __name__ =="__main__":
    app.run(debug=True, use_reloader=False)
    sess.init_app(app)
