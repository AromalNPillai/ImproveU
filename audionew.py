import os
import pyaudio
import wave
from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Global variables for recording
recording = False
stream = None
frames = []

# Route for home page
@app.route('/')
def index():
    return render_template('indexaudio.html')

# Route for starting and stopping recording
@app.route('/record', methods=['POST'])
def record():
    global recording, stream, frames

    if request.form['action'] == 'start':
        if not recording:
            # Start recording
            recording = True
            frames = []
            stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            
            while recording:
                data = stream.read(1024)
                frames.append(data)

        return '', 204

    elif request.form['action'] == 'stop':
        if recording:
            # Stop recording
            recording = False
            stream.stop_stream()
            stream.close()
            audio.terminate()

            # Save the recorded audio as a WAV file
            wf = wave.open('D:/interview_answer/recording.wav', 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
            wf.close()

        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
