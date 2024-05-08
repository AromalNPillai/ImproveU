import tkinter as tk
import pyttsx3
import openai
import pyaudio
import wave
import os
import glob
import speech_recognition as sr

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
OUTPUT_DIR = r"D:\interview answer"  # Specify the directory to save the recorded audio

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = None
frames = []

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
    question_text.delete('1.0', tk.END) 
    question_text.insert(tk.END, question)
    speak(question) 
    print(question)

def start_record():
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


def stop_record():
    global stream, frames
    stream.stop_stream()
    stream.close()
    # audio.terminate()
    
    # Delete the old audio file, if it exists
    old_audio_file = os.path.join(OUTPUT_DIR, WAVE_OUTPUT_FILENAME)
    if os.path.exists(old_audio_file):
        os.remove(old_audio_file)
        print("Old audio file deleted.")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    wf = wave.open(os.path.join(OUTPUT_DIR, WAVE_OUTPUT_FILENAME), 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("New audio file saved.")
    transcribe_audio()

def transcribe_audio():
    r = sr.Recognizer()
    audio_file_path = find_latest_audio_file(OUTPUT_DIR)
    if audio_file_path:
        with sr.AudioFile(audio_file_path) as source:
            audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language="en-IN") 
            print('Converting audio transcripts into text ...')
            print(text)
            write_to_file(text)
            submit_answer(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

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
    global first_question_flag, project_questions_count, question, datastructure_questions_count, networking_questions_count
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
        response_textbox.delete('1.0', tk.END)
        response_textbox.insert(tk.END, response_text)
        print(response_text)
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


# Create the main window
root = tk.Tk()
root.title("Interview Assistant")

# Create GUI elements
question_text = tk.Text(root, height=5, width=50)
question_text.pack(pady=10)

start_record_button = tk.Button(root, text="Start Record", command=start_record)
start_record_button.pack(pady=5)

stop_record_button = tk.Button(root, text="Stop Record", command=stop_record)
stop_record_button.pack(pady=5)

response_textbox = tk.Text(root, height=5, width=50)
response_textbox.pack(pady=10)

# Start the interview process
project_questions()

# Start the GUI main loop
root.mainloop()
