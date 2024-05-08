import pyaudio
import wave
import tkinter as tk
from threading import Thread
import speech_recognition as sr
import os
import glob
from datetime import datetime

class AudioTranscriber:
    def __init__(self):
        self.audio_file_path = None

        self.root = tk.Tk()
        self.root.title("Audio Transcriber")

        self.upload_button = tk.Button(self.root, text="Upload WAV File", command=self.upload_wav_file)
        self.upload_button.pack()

        self.transcribe_button = tk.Button(self.root, text="Transcribe", command=self.transcribe)
        self.transcribe_button.pack()
        self.transcribe_button.config(state=tk.DISABLED)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

    def upload_wav_file(self):
        self.audio_file_path = self.choose_latest_wav_file("D:/interview video")
        if self.audio_file_path:
            self.status_label.config(text="WAV file uploaded: " + self.audio_file_path)
            self.transcribe_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="No WAV files found in the specified directory")

    def choose_latest_wav_file(self, directory):
        wav_files = glob.glob(os.path.join(directory, "*.wav"))
        if wav_files:
            latest_file = max(wav_files, key=os.path.getctime)
            return latest_file
        else:
            return None

    def transcribe(self):
        if self.audio_file_path:
            self.status_label.config(text="Transcribing...")
            self.transcribe_audio(self.audio_file_path)
        else:
            self.status_label.config(text="No WAV file uploaded")

    def transcribe_audio(self, audio_file_path):
        r = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language="en-IN") 
            print('Converting audio transcripts into text ...')
            print(text)
            self.write_to_file(text)
            self.status_label.config(text="Transcription complete")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
            self.status_label.config(text="Transcription failed: Unable to understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            self.status_label.config(text="Transcription failed: Request error")

    def write_to_file(self, text):
        with open("transcribed_text.txt", "w") as file:
            file.write(text)
        print("Transcribed text saved to transcribed_text.txt")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    transcriber = AudioTranscriber()
    transcriber.run()