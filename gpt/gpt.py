import openai
import pyttsx3

def get_responce(prompt):
    API_KEY = "api-key"
    openai.api_key = API_KEY
    responce = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages= [
            {"role": "system", "content": "You are Technical Interviewer for a CS based company."},
            {"role": "user", "content": prompt}
        ],
    )

    return responce


def check_answer(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\n Is the answer right for the question? Also show an expected answer in a very short paragraph."
    return prompt

def generate_continuous_question(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\n Generate a question as a continuity for the question and answer given"
    return prompt



def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()



def project_questions():
    #answer = ""
    #with open("../transcribed_text.txt", "r") as file:
        #answers = file.readlines()
    question = "Tell me about your projects?"
    print(question)
    speak(question)
    

    answer = input("Enter Your answer : ")
    print(answer)
    prompt = generate_continuous_question(question, answer)
    response_object = get_responce(prompt)
    response = response_object.choices[0].message.content
    for _ in range(3):
        question = response
        print(question)
        speak(question)
        answer = input("Enter Your answer : ")
        check_out = check_answer(question, answer)
        response_object = get_responce(check_out)
        response = response_object.choices[0].message.content
        print(response)
        prompt = generate_continuous_question(question, answer)
        response_object = get_responce(prompt)
        response = response_object.choices[0].message.content

def oops_questions():
    question = "What is object oriented Programming?"
    print(question)
    speak(question)
    answer = input("Enter Answer : ")
    check_out = check_answer(question, answer)
    response_object = get_responce(check_out)
    response = response_object.choices[0].message.content
    print(response)
    prompt = generate_continuous_question(question, answer)
    response_object = get_responce(prompt)
    response = response_object.choices[0].message.content
    for _ in range(3):
        question = response
        print(question)
        speak(question)
        answer = input("Enter Your answer : ")
        check_out = check_answer(question, answer)
        response_object = get_responce(check_out)
        response = response_object.choices[0].message.content
        print(response)
        prompt = generate_continuous_question(question, answer)
        response_object = get_responce(prompt)
        response = response_object.choices[0].message.content



def algorithms_questions():
    res = get_responce("Ask the candidate questions to write a simple program to test their knowledge. Only question needed no heading or description.")
    question = res.choices[0].message.content
    print(question)
    speak(question)
    answer = input("Enter Answer : ")
    check_out = check_answer(question, answer)
    response_object = get_responce(check_out)
    response = response_object.choices[0].message.content
    print(response)
    prompt = generate_continuous_question(question, answer)
    response_object = get_responce(prompt)
    response = response_object.choices[0].message.content




def oops_questions():
    question = "What is object oriented Programming?"
    print(question)
    speak(question)
    answer = input("Enter Answer : ")
    check_out = check_answer(question, answer)
    response_object = get_responce(check_out)
    response = response_object.choices[0].message.content
    print(response)
    prompt = generate_continuous_question(question, answer)
    response_object = get_responce(prompt)
    response = response_object.choices[0].message.content
    for _ in range(3):
        question = response
        print(question)
        speak(question)
        answer = input("Enter Your answer : ")
        check_out = check_answer(question, answer)
        response_object = get_responce(check_out)
        response = response_object.choices[0].message.content
        print(response)
        prompt = generate_continuous_question(question, answer)
        response_object = get_responce(prompt)
        response = response_object.choices[0].message.content    


answer = ""
with open("./transcribed_text.txt", "r") as file:
    answers = file.readlines()

print(answer)

project_questions()
oops_questions()
algorithms_questions()