import openai
import pyttsx3
from gpt import gpt

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
    prompt = f"Question : {question}\nAnswer : {answer}\n Is the answer right for the question? Also show an expected answer in a very short paragraph."
    return prompt

def generate_continuous_question(question, answer):
    prompt = f"Question : {question}\nAnswer : {answer}\n Generate a question as a continuity for the question and answer given"
    return prompt



def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


# def project_questions(n):
#     with open("transcribed_text.txt", "r") as file:
#         answers = file.readlines()
#     questions = ["Tell me about your projects?"]
#     for question, answer in zip(questions, answers):
#         print(question)
#         speak(question)
#         answer = answer.strip()
#         print(answer)
#         input("Press Enter to continue to the next question...")
#         prompt = generate_continuous_question(question, answer)
#         response_object = get_response(prompt)
#         response = response_object.choices[0].message.content
#         print(response)
#         prompt = generate_continuous_question(question, answer)
#         response_object = get_response(prompt)
#         response = response_object.choices[0].message.content

# def oops_questions(n):
#     with open("transcribed_text.txt", "r") as file:
#         answers = file.readlines()
#     questions = ["What is object oriented Programming?"]
#     for question, answer in zip(questions, answers):
#         print(question)
#         speak(question)
#         answer = answer.strip()
#         print(answer)
#         input("Press Enter to continue to the next question...")
#         prompt = generate_continuous_question(question, answer)
#         response_object = get_response(prompt)
#         response = response_object.choices[0].message.content
#         print(response)
#         prompt = generate_continuous_question(question, answer)
#         response_object = get_response(prompt)
#         response = response_object.choices[0].message.content

# def algorithms_questions(n):
#     with open("transcribed_text.txt", "r") as file:
#         answers = file.readlines()
#     res = get_response("Ask the candidate questions to write a simple program to test their knowledge. Only question needed no heading or description.")
#     question = res.choices[0].message.content
#     print(question)
#     speak(question)
#     for answer in answers:
#         input("Press Enter to continue to the next answer...")
#         answer = answer.strip()
#         check_out = check_answer(question, answer)
#         response_object = get_response(check_out)
#         response = response_object.choices[0].message.content
#         print(response)
#         prompt = generate_continuous_question(question, answer)
#         response_object = get_response(prompt)
#         response = response_object.choices[0].message.content


gpt.project_questions()
gpt.oops_questions()
gpt.algorithms_questions()
