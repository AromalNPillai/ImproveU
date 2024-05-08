from flask import Flask, render_template, Response, redirect, request, url_for, session, jsonify
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


question_to_send = ""

first_question_flag = 0
project_questions_count = 0
datastructure_questions_count = 0
networking_questions_count = 0
question = "Tell me about your projects?"
ts = 0

# Constants for recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5  # Adjust as needed
WAVE_OUTPUT_FILENAME = "output.wav"
OUTPUT_DIR = "interview_answer"  # Specify the directory to save the recorded audio

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = None
frames = []

question_text = None
output_text = None

app = Flask(__name__)
app.secret_key = 'qwertyuidfgbnmpijbshjdbs'
app.config["SESSION_PERMANENT"] = False

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="arya bhavan",
    database="flask_users"
)
cursor = db.cursor()

mp_face = mp.solutions.face_detection
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

head_tilt_buffer = deque(maxlen=10)
shoulder_buffer = deque(maxlen=10)

cap = cv2.VideoCapture(0)
recording = False
video_out = None
audio_out = None

baseline_shoulder_height = None

def generate_frames():
    global recording, video_out, audio_out
    with open("looking.txt", 'w') as wfile:
        wfile.write("")

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
                head_tilt_text = "Wrong Posture"
                with open("looking.txt", 'a') as afile:
                    afile.write("Wrong Posture\n")
            else:
                head_tilt_text = "Correct Posture"
                with open("looking.txt", 'a') as afile:
                    afile.write("Correct Posture\n")

        
            # cv2.putText(frame, head_tilt_text, (frame.shape[1] - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (125, 125, 125), 2)

            if -25 < avg_head_tilt_left_eye < 25 or -25 < avg_head_tilt_right_eye < 25:  
                posture_text = "Correct Posture"
                with open("looking.txt", 'a') as afile:
                    afile.write("Correct Posture\n")
            else:
                posture_text = "Wrong Posture"
                with open("looking.txt", 'a') as afile:
                    afile.write("Wrong Posture\n")

            cv2.putText(frame, posture_text, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


        if holistic_results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, holistic_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            global baseline_shoulder_height

            left_shoulder = holistic_results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = holistic_results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER]

            left_shoulder_y = left_shoulder.y * frame.shape[0]
            right_shoulder_y = right_shoulder.y * frame.shape[0]

            if baseline_shoulder_height is None:
                baseline_shoulder_height = (left_shoulder_y + right_shoulder_y) / 2

            current_shoulder_height = (left_shoulder_y + right_shoulder_y) / 2

            shoulder_raise_threshold = 0.05  

            if current_shoulder_height < baseline_shoulder_height - shoulder_raise_threshold:
                shoulder_text = "Wrong Posture"
                shoulder_buffer.append(True)
                with open("Looking.txt", 'a') as afile:
                    afile.write("Wrong   Posture\n")
            else:
                shoulder_text = "Correct Posture"
                shoulder_buffer.append(False)
                with open("Looking.txt", 'a') as afile:
                    afile.write("Correct Posture\n")

            cv2.putText(frame, shoulder_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
           
            with open('Looking.txt', 'r') as file:
    # Read all lines
                lines = file.readlines()

            # Initialize counters
            total_count = 0
            correct_posture_count = 0

            # Loop through each line
            for line in lines:
                # Strip any leading/trailing whitespace
                line = line.strip()
                # If the line indicates correct posture, count it
                if line == 'Correct Posture':
                    correct_posture_count += 1
                # Always count total lines
                total_count += 1

            # Calculate the accuracy percentage
            accuracy_percentage = (correct_posture_count / total_count) * 100

            # Print the result
            # print("Total count:", total_count)
            # print("Correct Posture count:", correct_posture_count)
            # print("Accuracy percentage:", accuracy_percentage)

            with open('posturefinal.txt', 'w') as result_file:
                result_file.write("Total count: {}\n".format(total_count))
                result_file.write("Correct Posture count: {}\n".format(correct_posture_count))
                result_file.write("Accuracy percentage: {:.2f}%\n".format(accuracy_percentage))


        

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

def project_questions():
    global project_questions_count, question
    if project_questions_count < 3:
        update_question(question)
    else:
        datastructure_questions()


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
            session.clear()
            session['username'] = user[1]
            session['email'] = user[3]
            return redirect(url_for('admindash'))
        elif user:
            session.clear()
            session['username'] = user[1]
            session['email'] = user[3]
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
    return render_template('index3.html', start_state=False)

@app.route('/about')
def about():
    username = session.get("username")
    email = session.get("email")
    cursor.execute(f"SELECT interview_score, posture_score FROM record WHERE st_id='{username}';")
    record = cursor.fetchall()
    print(record)
    return render_template('about.html', start_state=False, username=username, email=email, records = record)

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/start')
def start_interview():
    with open('openai_response.txt', 'w') as wfile:
        wfile.write("Tell me about your projects?\n")
    project_questions()
    return render_template('index3.html', start_state=True)


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
    global recording, video_out, audio_out

    recording = False

    if video_out is not None:
        video_out.release()
        video_out = None

    if audio_out is not None:
        audio_out.close()
        audio_out = None

    return redirect('/')


import os
from threading import Thread
import speech_recognition as sr

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_file_path = ""

    def start_record(self):
        self.recording = True
        self.record_thread = Thread(target=self.record_audio)
        self.record_thread.start()

    def stop_record(self):
        self.recording = False

    def record_audio(self):
        directory = r"D:\interview answer"  # Default directory
        file_path = os.path.join(directory, "recorded_audio.wav")

        audio = pyaudio.PyAudio()

        sample_rate = 44100
        chunk_size = 1024
        format = pyaudio.paInt16
        channels = 2

        stream = audio.open(format=format,
                            channels=channels,
                            rate=sample_rate,
                            input=True,
                            frames_per_buffer=chunk_size)

        frames = []

        while self.recording:
            data = stream.read(chunk_size)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wave_file = wave.open(file_path, 'wb')
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(audio.get_sample_size(format))
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        self.audio_file_path = file_path
        self.transcribe_audio()

        # Delete the old audio file
        if os.path.exists(self.audio_file_path):
            os.remove(self.audio_file_path)

    # def transcribe_audio(self):
    #     r = sr.Recognizer()
    #     with sr.AudioFile(self.audio_file_path) as source:
    #         audio_text = r.listen(source)
    #     try:
    #         text = r.recognize_google(audio_text, language="en-IN")
    #         print('Converting audio transcripts into text ...')
    #         print(text)
    #         self.write_to_file(text)
    #     except sr.UnknownValueError:
    #         print("Google Speech Recognition could not understand the audio")
    #     except sr.RequestError as e:
    #         print("Could not request results from Google Speech Recognition service; {0}".format(e))

    # def write_to_file(self, text):
        # with open("transcribed_text.txt", "w") as file:
        #     file.write(text)
    #     print("Transcribed text saved to transcribed_text.txt")


    def transcribe_audio(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.audio_file_path) as source:
            audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language="en-IN")
            print('Converting audio transcripts into text ...')
            print(text)
            # Append the transcribed text to the openai_response.txt file
            with open("openai_response.txt", "a") as file:
                file.write(text + "\n")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


recorder = AudioRecorder()

@app.route('/start_record')
def start_record():
    recorder.start_record()
    return jsonify({"message": "Recording started"})




import time

@app.route('/submit_answer', methods=['POST'])
# def submit_answer_route():
#     global question_text, output_text
#     answer = request.form['answer']
#     submit_answer(answer)  # Call the function to process the answer
#     with open('result.txt', 'a') as afile:
#         afile.write(f"\nOptimal answer : {output_text} \n\nQuestion : {question_text}")
#     return jsonify({'body': {'question': question_text, 'answer' : output_text}})

def submit_answer_route():
    global question_text, output_text
    answer = request.form['answer']
    
    # Write the question to the openai_response.txt file
    with open('openai_response.txt', 'a') as file:
        if not question_text == "Tell me about your projects?":
            file.write(f"Question: {question_text}\n")
    
    submit_answer(answer)  # Call the function to process the answer
    
    # Write the optimal answer and question to the result.txt file
    with open('openai_response.txt', 'a') as afile:
        afile.write(f"Question: {question_text}\nOptimal answer: {output_text}\n")
    
    return jsonify({'body': {'question': question_text, 'answer' : output_text}})


def generate_continuous_question(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\nGenerate a question as a continuity for the question and answer given"
    return prompt

import openai

def get_response(prompt):
    API_KEY = ""
    openai.api_key = API_KEY
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Technical Interviewer for a CS based company."},
            {"role": "user", "content": prompt}
        ],
    )

    return response

def update_question(question):
    global question_text
    question_text = question
    speak(question)  # Speak the question
    print(question)

import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def check_answer(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\nIs the answer right for the question? Also show an expected answer in a very short paragraph and also provide a score out of 100. be very strict in the scoring. the scoring should be based on how right the answer is for the question. check the answer based on general keywords"
    return prompt

def generate_continuous_question(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\nGenerate a question as a continuity for the question and answer given"
    return prompt

def project_questions():
    global project_questions_count, question
    if project_questions_count < 3:
        update_question(question)
    else:
        datastructure_questions()

def datastructure_questions():
    res = get_response("Ask the candidate questions about Data Structures and Algorithms. Only question needed no heading or description.")
    question = res.choices[0].message.content
    update_question(question)

def networking_questions():
    res = get_response("Ask the candidate questions about Networking. Only question needed no heading or description.")
    question = res.choices[0].message.content
    update_question(question)

def update_question(question):
    global question_text
    question_text = question
    speak(question)  # Speak the question
    print(question)


def start_recording():  # Renamed to start_recording
    global stream, frames
    frames = []
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording started...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording finished.")

#

total_score = 0

# def submit_answer(answer):
#     global total_score, first_question_flag, project_questions_count, question, datastructure_questions_count, networking_questions_count
    
#     if first_question_flag == 0:
#         prompt = generate_continuous_question(question, answer)
#         response = get_response(prompt)
#         response_text = response.choices[0].message.content
#         first_question_flag = 1
#         update_question(response_text)
#     else:
#         check_out = check_answer(question, answer)
#         response = get_response(check_out)
#         response_text = response.choices[0].message.content
#         print(response_text)

#         # Evaluate the answer and update the total score
#         score = evaluate_answer(question, answer)
#         total_score += score

#         project_questions_count += 1
#         if project_questions_count < 3:
#             prompt = generate_continuous_question(question, answer)
#             response = get_response(prompt)
#             response_text = response.choices[0].message.content
#             update_question(response_text)
#         elif datastructure_questions_count< 3:
#             datastructure_questions()
#             datastructure_questions_count += 1
#         elif networking_questions_count < 3:
#             networking_questions()
#             networking_questions_count += 1

#     print("Total Score:", total_score)


def submit_answer(answer):
    global total_score, first_question_flag, project_questions_count, question, datastructure_questions_count, networking_questions_count
    
    if first_question_flag == 0:
        prompt = generate_continuous_question(question, answer)
        response = get_response(prompt)
        response_text = response.choices[0].message.content
        first_question_flag = 1
        update_question(response_text)
    else:
        check_out = check_answer(question, answer)
        response = get_response(check_out)
        response_text = response.choices[0].message.content
        print(response_text)

        # Write the response to a text file
        with open('openai_response.txt', 'a') as file:
            file.write(response_text + '\n')

        # Evaluate the answer and update the total score
        score = evaluate_answer(question, answer)
        total_score += score

        project_questions_count += 1
        if project_questions_count < 3:
            prompt = generate_continuous_question(question, answer)
            response = get_response(prompt)
            response_text = response.choices[0].message.content
            update_question(response_text)
        elif datastructure_questions_count < 3:
            datastructure_questions()
            datastructure_questions_count += 1
        elif networking_questions_count < 3:
            networking_questions()
            networking_questions_count += 1

    print("Total Score:", total_score)


def evaluate_answer(question, answer):
    # This is a placeholder for your evaluation function
    # You can implement this function to evaluate the correctness of the answer
    # and assign a score accordingly
    # For now, let's just return a random score between 0 and 10
    import random
    return random.randint(0, 10)


@app.route('/stop_record')
def stop_record():
    recorder.stop_record()
    time.sleep(5)
    with open('openai_response.txt', 'r') as rfile:
        text = rfile.read()
    with open('result.txt', 'a') as afile:
        afile.write(f"\n Answer : {text}")
    return jsonify({"message": "Recording stopped", 'text' : text})

def generate_review(interview_score, posture_score):
    # Logic to generate review based on interview score and posture score
    if interview_score >= 8 and posture_score >= 8:
        return "Excellent! You have shown great improvement in both your interview performance and posture. Keep up the good work!"
    elif interview_score >= 6 and posture_score >= 6:
        return "Good job! Your interview performance and posture are improving steadily. Keep practicing for better results."
    elif interview_score >= 4 and posture_score >= 4:
        return "You're making progress, but there's still room for improvement in both your interview performance and posture. Keep working on it!"
    else:
        return "There is significant room for improvement in both your interview performance and posture. Consider seeking further guidance and practice."


    
@app.route('/finish')
# def finish():
#     return render_template('index2.html')

# def finish():
#     # Clear the contents of openai_response.txt

#     with open('openai_response.txt', 'w') as file:
#         pass  # Writing nothing to the file effectively clears it

#     return render_template('index2.html')




def finish():
    # Read the contents of openai_response.txt and filter out blank lines
    # with open('openai_response.txt', 'r') as file:
    #     lines = file.readlines()
        # non_blank_lines = [line for line in lines if line.strip()]

    # # Write the non-blank lines back to openai_response.txt
    # with open('openai_response.txt', 'w') as file:
    #     file.writelines(non_blank_lines)



    with open('result.txt', 'w') as file:
        pass
    # Print the total score
    global ts
    ts = calculate_total_score(file_path)
    print("Total Score:", ts)
    with open('openai_response.txt', 'r') as source:
        with open('result.txt', 'w') as destination:
            destination.write(source.read())

    # Clear the contents of openai_response.txt
    with open('openai_response.txt', 'w') as file:
        pass  # Writing nothing to the file effectively clears it

    # Render the index2.html template
    return render_template('index2.html')


def calculate_total_score(file_path):
    # Initialize total score
    total_score = 0
    
    try:
    # Open the file for reading
        with open(file_path, 'r') as file:
            # Initialize total_score
            total_score = 0
            # Read each line in the file
            for line in file:
                # Check if the line contains the pattern 'Score:'
                if 'Score:' in line:
                    try:
                        # Extract the score from the line
                        score_str = line.split(':')[1].strip()
                        # Convert the score to an integer
                        score = int(score_str.split('/')[0])
                        # Add the score to the total score
                        total_score += score
                    except ValueError:
                        print("Error: Unable to convert score to an integer.")
                        # Handle the error as needed
                    except IndexError:
                        print("Error: Index out of range while splitting the score string.")
                        # Handle the error as needed
    except FileNotFoundError:
        print("Error: File not found.")
        # Handle the error as needed
    except Exception as e:
        print("An error occurred:", e)
        # Handle other exceptions as needed

    
    except FileNotFoundError:
        print("File not found.")
    
    return total_score

# Call the function with the file path
file_path = 'openai_response.txt'

# Print the total score
print("Total Score:", total_score)




@app.route('/analysis')
def resulttext():
    global ts
    with open('posturefinal.txt', 'r') as file:
        file_contents = file.read()
        file_contents = file_contents.replace('\n', '<br>')

    with open("openai_response.txt", 'r') as rfile:
        content = rfile.read()
        content = content.replace("\n", "<br>")


                # Read the review file
    with open('openai_response.txt', 'r') as file:
        review_content = file.readlines()

    total_score = 0

    # Iterate through each line in the review content
    for line in review_content:
        # Check if the line contains a score
        if line.startswith('Score:'):
            # Extract the score part from the line
            score_part = line.split(':')[1].strip()
            # Extract the actual score value from the score part
            score = int(score_part.split('/')[0].strip())
            # Add the score to the total score
            total_score += score

    # Write the total score to a new file
    with open('total_score.txt', 'w') as file:
        file.write(f'Total Score: {total_score}')

    print('Total score saved to total_score.txt')

    with open("total_score.txt", "r") as rfile:
        score = rfile.read()

    cursor.execute(f"SELECT * FROM tbl_users WHERE username=\"{session.get('username')}\";")
    user = cursor.fetchone()

    print(user)
    cursor.execute(f"INSERT INTO record VALUES(\'{user[1]}\', '{score}', '{file_contents}');")
    db.commit()

    print(file_contents)
    return render_template('analysis.html', file_contents=file_contents, review = ts, answers = content, score=score)






@app.route('/review', methods=['POST'])
def review():
    session['interview_score'] = int(request.form['interview_score'])
    session['posture_score'] = int(request.form['posture_score'])
    return redirect(url_for('analysis'))

@app.route('/analysis')
def analysis():
    print("HEREREREERER")
    if 'interview_score' not in session or 'posture_score' not in session:
        return redirect(url_for('userdash'))

    interview_score = session['interview_score']
    posture_score = session['posture_score']

    prev_interview_score = session.get('prev_interview_score', None)
    prev_posture_score = session.get('prev_posture_score', None)

    if prev_interview_score is None or prev_posture_score is None:
        session['prev_interview_score'] = interview_score
        session['prev_posture_score'] = posture_score
        return render_template('analysis.html', review=generate_review(interview_score, posture_score), prev_review=None)

    prev_review = generate_review(prev_interview_score, prev_posture_score)
    new_review = generate_review(interview_score, posture_score)

    session['prev_interview_score'] = interview_score
    session['prev_posture_score'] = posture_score
    with open('result.txt', 'r') as rfile:
        out = rfile.read()

    with open("total_score.txt", 'r') as rfile:
        score = rfile.read()
    print("HERE", score)

    return render_template('analysis.html', review=new_review, prev_review=prev_review, file_out = out, score=score)

if __name__ == "__main__":
    with mp_face.FaceDetection(min_detection_confidence=0.5) as face_detection, \
            mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        app.run(debug=True)
