from flask import Flask, redirect, request, render_template, Response
import cv2
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import re
from main import *
from ocr_detection import ocr_it, save_results
import os

app = Flask(__name__)
app.secret_key = 'the random string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/npd'
app.config["UPLOAD_FOLDER"] = "D:\\Projects\\RealTimeObjectDetection\\static\\video"
db = SQLAlchemy(app)
global switch
switch = 0
global video_path
video_path = "D:\\Projects\\RealTimeObjectDetection\\static\\video\\sample.mp4"


class Numbers_plates(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    time = db.Column(db.String(20), nullable=True)


cap = cv2.VideoCapture()
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


def validString(str):
    if len(str) == 0:
        return str
    str = str.replace(" ", "")
    str = str.replace("-", "")
    str = str.replace(".", "")
    if len(str) == 9:
        str1 = str[:2] + '-' + str[2:4] + '-' + str[4:5] + '-' + str[5:]
        if str1[3] == 'o' or str1[3] == 'O':
            temp = list(str1)
            temp[3] = "0"
            str1 = "".join(temp)
        return str1
    else:
        str1 = str[:2] + '-' + str[2:4] + '-' + str[4:6] + '-' + str[6:]
        if str1[3] == 'o' or str1[3] == 'O':
            temp = list(str1)
            temp[3] = "0"
            str1 = "".join(temp)
        return str1
def isValidLicenseNo(str):
    if len(str) == 12:
        regex = ("[A-Z]{2}[-][0-9]{2}[-][A-Z]{1}[-][0-9]{4}$")
        p = re.compile(regex)
        if (re.search(p, str)):
            return True
        else:
            return False
    else:
        regex = ("[A-Z]{2}[-][0-9]{2}[-][A-Z]{2}[-][0-9]{4}$")
        p = re.compile(regex)
        if (re.search(p, str)):
            return True
        else:
            return False


def generate_frames():
    temp_number = "xx-xx-xxxx"
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        else:
            image_np = np.array(frame)
            input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
            detections = detect_fn(input_tensor)
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                          for key, value in detections.items()}
            detections['num_detections'] = num_detections
            # detection_classes should be ints.
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
            label_id_offset = 1
            image_np_with_detections = image_np.copy()
            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detections['detection_boxes'],
                detections['detection_classes'] + label_id_offset,
                detections['detection_scores'],
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=5,
                min_score_thresh=.8,
                agnostic_mode=False)
            text = ocr_it(image_np_with_detections, detections, detection_threshold, region_threshold)
            if text is None:
                pass
            else:
                num_plate = ""
                for i in text:
                    num_plate += i
                number_plate = validString(num_plate.upper())
                isvalid = isValidLicenseNo(number_plate)
                if isvalid == True:
                    if number_plate == temp_number:
                        continue
                    else:
                        temp_number = number_plate
                        save_results(number_plate)
                else:
                    pass
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    rows = Numbers_plates.query.filter_by().all()[0:5]
    return render_template('main.html', rows=rows)


@app.route('/requests', methods=["GET", "POST"])
def tasks():
    global switch, cap
    if request.method == "POST":
        request.form.get('stop') == 'Stop/Start'
        if (switch == 1):
            cap.release()
            cv2.destroyAllWindows()
            switch = 0
        else:
            cap = cv2.VideoCapture(video_path)
            # cap = cv2.VideoCapture('https://192.168.43.1:8080/video')
            switch = 1
    return redirect('/#app')


@app.route('/video/')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/date-filter", methods=["GET", "POST"])
def date_filed():
    if request.method == "POST":
        date1 = request.form.get('date1')
        date2 = request.form.get('date2')
        if (date1):
            rows = Numbers_plates.query.filter_by(date=date1)
        if (date1 and date2):
            rows = Numbers_plates.query.filter(Numbers_plates.date.between(date1, date2)).all()
    return render_template('data.html', rows=rows)


@app.route("/time-filter", methods=["GET", "POST"])
def time_field():
    if request.method == "POST":
        time1 = request.form.get('time1')
        time2 = request.form.get('time2')
        date_time = request.form.get('date_time')
        if (date_time and time1 and time2):
            rows = Numbers_plates.query.filter(Numbers_plates.time.between(time1, time2)).filter_by(date=date_time).all()
    return render_template('data.html', rows=rows)


@app.route('/uploder', methods=["GET", "POST"])
def uploader():
    if request.method == "POST":
        file = request.files["myfile"]
        filename = 'sample.mp4'
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return redirect('requests')


if __name__ == "__main__":
    app.run(debug=True)
