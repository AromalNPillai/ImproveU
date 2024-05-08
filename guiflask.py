from flask import Flask, render_template, request, jsonify
import pyttsx3
import openai
import pyaudio
import wave
import os
import glob
import speech_recognition as sr

app = Flask(__name__)

question_to_send = ""

first_question_flag = 0
project_questions_count = 0
datastructure_questions_count = 0
networking_questions_count = 0
question = "Tell me about your projects?"

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

def get_response(prompt):
    API_KEY = "api-key"
    openai.api_key = API_KEY
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Technical Interviewer for a CS based company."},
            {"role": "user", "content": prompt}
        ],
    )

    return response

def check_answer(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\nIs the answer right for the question? Also show an expected answer in a very short paragraph."
    return prompt

def generate_continuous_question(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\nGenerate a question as a continuity for the question and answer given"
    return prompt

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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

@app.route('/')
def index():
    project_questions()
    return render_template('index96.html', question=question)

# @app.route('/start_record', methods=['POST'])
# def start_record_route():
#     start_recording()
#     return '', 204

# @app.route('/stop_record', methods=['POST'])
# def stop_record_route():
#     stop_record()
#     return '', 204

import json

@app.route('/submit_answer', methods=['POST'])
def submit_answer_route():
    global question_text, output_text
    answer = request.form['answer']
    submit_answer(answer)  # Call the function to process the answer
    return jsonify({'body': {'question': question_text, 'answer' : output_text}})

# def stop_record():
#     global stream, frames
#     stream.stop_stream()
#     stream.close()
#     # audio.terminate()
    
#     # Delete the old audio file, if it exists
#     old_audio_file = os.path.join(OUTPUT_DIR, WAVE_OUTPUT_FILENAME)
#     if os.path.exists(old_audio_file):
#         os.remove(old_audio_file)
#         print("Old audio file deleted.")

#     if not os.path.exists(OUTPUT_DIR):
#         os.makedirs(OUTPUT_DIR)
#     wf = wave.open(os.path.join(OUTPUT_DIR, WAVE_OUTPUT_FILENAME), 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(audio.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()

#     print("New audio file saved.")
#     transcribe_audio()

from threading import Thread


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

    def transcribe_audio(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.audio_file_path) as source:
            audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language="en-IN")
            print('Converting audio transcripts into text ...')
            print(text)
            self.write_to_file(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def write_to_file(self, text):
        with open("transcribed_text.txt", "w") as file:
            file.write(text)
        print("Transcribed text saved to transcribed_text.txt")

recorder = AudioRecorder()
import time

@app.route('/start_record')
def start_record():
    recorder.start_record()
    return jsonify({"message": "Recording started"})

@app.route('/stop_record')
def stop_record():
    recorder.stop_record()
    time.sleep(5)
    with open('transcribed_text.txt', 'r') as rfile:
        text = rfile.read()
    return jsonify({"message": "Recording stopped", 'text' : text})





def find_latest_audio_file(directory):
    wav_files = glob.glob(os.path.join(directory, "*.wav"))
    if wav_files:
        return max(wav_files, key=os.path.getctime)
    else:
        return None

def write_to_file(text):
    with open("transcribed_text.txt", "w") as file:
        file.write(text)
    print("Transcribed text saved to transcribed_text.txt")

def submit_answer(answer):
    global first_question_flag, project_questions_count, question, datastructure_questions_count, networking_questions_count, question, output_text
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
        # response_textbox.delete('1.0', tk.END)
        # response_textbox.insert(tk.END, response_text)
        print(response_text)
        output_text = response_text
        project_questions_count += 1
        if project_questions_count < 3:
            prompt = generate_continuous_question(question, answer)
            response = get_response(prompt)
            response_text = response.choices[0].message.content
            update_question(response_text)
        elif datastructure_questions_count< 3:
            datastructure_questions()
            datastructure_questions_count += 1
        elif networking_questions_count < 3:
            networking_questions()
            networking_questions_count += 1

if __name__ == '__main__':
    app.run(debug=True)
