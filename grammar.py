from gramformer import Gramformer
import torch
import re

def set_seed(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(1212)

gf = Gramformer(models=1, use_gpu=False)  

input_file_path = "transcribed_text.txt"

with open(input_file_path, "r") as file:
    influent_sentences = file.readlines()

influent_sentences = [sentence.strip() for sentence in influent_sentences]

for influent_sentence in influent_sentences:
    corrected_sentences = gf.correct(influent_sentence, max_candidates=1)
    print("[Input] ", influent_sentence)
    for corrected_sentence in corrected_sentences:
        corrected_sentence = re.sub(r'[^\w\s]', '', corrected_sentence)  # Remove trailing punctuation
        print("[Correction] ", corrected_sentence)
    print("-" * 100)
