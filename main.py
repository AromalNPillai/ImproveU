from flask import Flask, render_template, Response, redirect, request, url_for
import cv2
import mediapipe as mp
import math
from collections import deque
from datetime import datetime
import pyaudio
import wave
import threading
import numpy as np
import mysql.connector

app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="arya bhavan",
    database="flask_users"
)
cursor = db.cursor()

# MediaPipe Initialization
mp_face = mp.solutions.face_detection
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Video Capture Initialization
cap = cv2.VideoCapture(0)

# Global Variables for Recording
recording = False
video_out = None
audio_out = None

# Head Tilt Buffer for Posture Detection
head_tilt_buffer = deque(maxlen=10)

def generate_frames():
    global recording, video_out, audio_out

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_results = face_detection.process(rgb_frame)
        holistic_results = holistic.process(rgb_frame)

        # Face Detection
        if face_results.detections:
            for detection in face_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)

                cv2.rectangle(frame, bbox, (255, 0, 255), 2)

        # Holistic Landmarks Detection
        if holistic_results.face_landmarks:
            mp_drawing.draw_landmarks(frame, holistic_results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
            mp_drawing.draw_landmarks(frame, holistic_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            nose_landmark = holistic_results.face_landmarks.landmark[5]
            left_eye_landmark = holistic_results.face_landmarks.landmark[33]
            right_eye_landmark = holistic_results.face_landmarks.landmark[263]

            angle_nose_left_eye = math.degrees(math.atan2(left_eye_landmark.y - nose_landmark.y, left_eye_landmark.x - nose_landmark.x))
            angle_nose_right_eye = math.degrees(math.atan2(right_eye_landmark.y - nose_landmark.y, right_eye_landmark.x - nose_landmark.x))

            head_tilt_buffer.append((angle_nose_left_eye, angle_nose_right_eye))

            avg_head_tilt_left_eye, avg_head_tilt_right_eye = zip(*head_tilt_buffer)
            avg_head_tilt_left_eye = sum(avg_head_tilt_left_eye) / len(avg_head_tilt_left_eye)
            avg_head_tilt_right_eye = sum(avg_head_tilt_right_eye) / len(avg_head_tilt_right_eye)

            if avg_head_tilt_left_eye < -15 and avg_head_tilt_right_eye < -15:
                head_tilt_text = "Looking Down"
            else:
                head_tilt_text = "Looking Straight"

            cv2.putText(frame, head_tilt_text, (frame.shape[1] - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if -25 < avg_head_tilt_left_eye < 25 or -25 < avg_head_tilt_right_eye < 25:  
                posture_text = "Correct Posture"
            else:
                posture_text = "Wrong Posture"

            cv2.putText(frame, posture_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Video Recording
        if recording:
            if video_out is None:
                output_dir = r"D:\interview video"
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                video_file_name = f'{output_dir}/output_{current_time}.mp4'
                video_out = cv2.VideoWriter(video_file_name, cv2.VideoWriter_fourcc(*'mp4v'), 10.0, (frame.shape[1], frame.shape[0]))

                audio_file_name = f'{output_dir}/output_{current_time}.wav'
                audio_out = wave.open(audio_file_name, 'wb')
                audio_out.setnchannels(1)
                audio_out.setsampwidth(2)
                audio_out.setframerate(44100)

                audio_thread = threading.Thread(target=capture_audio)
                audio_thread.start()

            video_out.write(frame)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def capture_audio():
    global recording, audio_out

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        if recording and audio_out is not None:
            data = stream.read(CHUNK)
            audio_out.writeframes(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

@app.route('/')
def index():
    return render_template('userlogin.html')

@app.route('/userlogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM tbl_admin WHERE username = %s AND password = %s', (username, password))
        admin = cursor.fetchone()

        cursor.execute('SELECT * FROM tbl_users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if admin:
            return redirect(url_for('admindash'))
        elif user:
            return redirect(url_for('userdash'))
        else:
            return render_template('userlogin.html', error='Invalid username or password')

    return render_template('userlogin.html')

@app.route('/userdash')
def userdash():
    return render_template('userdash.html')

@app.route('/admindash')
def admindash():
    cursor.execute('SELECT id, username, email FROM tbl_users')
    users = cursor.fetchall()
    users = [list(user) for user in users]
    return render_template('admindash.html', users=users)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    cursor.execute('DELETE FROM tbl_users WHERE id = %s', (id,))
    db.commit()
    return redirect(url_for('admindash'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor.execute('INSERT INTO tbl_users (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
        db.commit()
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/index3')
def index3():
    return render_template('index3.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording
    recording = True
    return 'Recording Started'

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, video_out, audio_out

    recording = False

    if video_out is not None:
        video_out.release()
        video_out = None

    if audio_out is not None:
        audio_out.close()
        audio_out = None

    return 'Recording Stopped'

if __name__ == "__main__":
    with mp_face.FaceDetection(min_detection_confidence=0.5) as face_detection, \
            mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        app.run(debug=True)
