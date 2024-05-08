from flask import Flask, render_template, Response, request
import cv2
import mediapipe as mp
import math
from collections import deque
from datetime import datetime
from flask import Flask, render_template, Response, redirect

app = Flask(__name__)

mp_face = mp.solutions.face_detection
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

head_tilt_buffer = deque(maxlen=10)

cap = cv2.VideoCapture(0)
recording = False
out = None

def generate_frames():
    global recording, out

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_results = face_detection.process(rgb_frame)

        holistic_results = holistic.process(rgb_frame)

        if face_results.detections:
            for detection in face_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)

                cv2.rectangle(frame, bbox, (255, 0, 255), 2)

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

        if recording:
            if out is None:
                output_dir = r"D:\interview video"
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_name = f'{output_dir}/output_{current_time}.avi'
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(file_name, fourcc, 10.0, (frame.shape[1], frame.shape[0]))

            out.write(frame)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording
    recording = True
    return redirect('/')


@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, out
    recording = False
    if out is not None:
        out.release()
        out = None
    return redirect('/')


if __name__ == "__main__":
    with mp_face.FaceDetection(min_detection_confidence=0.5) as face_detection, \
            mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        app.run(debug=True)