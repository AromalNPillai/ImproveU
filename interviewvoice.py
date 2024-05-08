from flask import Flask, render_template, jsonify
from threading import Thread
import os
import pyaudio
import wave
import speech_recognition as sr

app = Flask(__name__)
    
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

@app.route('/')
def index():
    return render_template('index69.html')

@app.route('/start_record')
def start_record():
    recorder.start_record()
    return jsonify({"message": "Recording started"})

@app.route('/stop_record')
def stop_record():
    recorder.stop_record()
    return jsonify({"message": "Recording stopped"})

if __name__ == "__main__":
    app.run(debug=True)