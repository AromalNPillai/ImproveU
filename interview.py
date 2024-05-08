import pyttsx3
import json
from gpt.gpt import *

def ask_question():
    engine = pyttsx3.init()
    question = "Introduce Yourself"
    print(question)
    engine.say(question)
    engine.runAndWait()
    answer = input("Your answer: ")
    question = "Tell me about your projects?"
    print(question)
    engine.say(question)
    engine.runAndWait()
    answer = input("Your answer: ")
    prompt = generate_continuous_question(question, answer)
    response_object = get_responce(prompt)
    response = response_object.choices[0].message.content
    for _ in range(3):
        question = response
        print(question)
        engine.say(question)
        engine.runAndWait()
        answer = input("Your answer: ")
        check_out = check_answer(question, answer)
        response_object = get_responce(check_out)
        response = response_object.choices[0].message.content
        print(response)
        prompt = generate_continuous_question(question, answer)
        response_object = get_responce(prompt)
        response = response_object.choices[0].message.content

    # keywords = question_obj.get('keywords', [])  # Retrieve keywords associated with the question from JSON
    # if any(keyword in answer for keyword in keywords):  # Check if any keyword is in the answer
    #     return True  # Return True if answer contains any keyword
    # else:
    #     return False  # Return False if answer doesn't contain any keyword

# def main():
#     with open('interview_questions.json', 'r') as file:
#         data = json.load(file)

#     questions = data['questions']

#     for question_obj in questions:
#         if ask_question(question_obj):  # Check the return value of ask_question
#             print("correct answer")
#         else:
#             print("incorrect answer")

if __name__ == "__main__":
    ask_question()
    