
import json
import os
import Levenshtein
import re
from difflib import SequenceMatcher
import re
import difflib
from difflib import ndiff
import string
def extract_text_from_json(data, results=None):
    if results is None:
        results = []

    if isinstance(data, dict):
        if 'text' in data:
            # If the key 'text' exists in the dictionary, extract its value
            results.append(data['text'])
        else:
            # Continue traversing nested dictionaries
            for value in data.values():
                extract_text_from_json(value, results)

    elif isinstance(data, list):
        # Continue searching inside lists
        for item in data:
            extract_text_from_json(item, results)
    return results

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)



def extract_tokens(text):
    if not isinstance(text, str):
        text = str(text)  # Ensure conversion to string
    return re.findall(r'\d+\.\d+|\d+|\w+', text)


def highlight_numbers(text1, text2):
    numbers1 = set(re.findall(r'\d+\.\d+|\d+', text1))
    numbers2 = set(re.findall(r'\d+\.\d+|\d+', text2))

    diff = list((numbers1 - numbers2) | (numbers2 - numbers1))
    return diff

def weighted_similarity(text1, text2):
    tokens1, tokens2 = extract_tokens(text1), extract_tokens(text2)

    num1 = set(re.findall(r'\d+\.\d+|\d+', text1))
    num2 = set(re.findall(r'\d+\.\d+|\d+', text2))

    num_similarity = len(num1 & num2) / max(len(num1 | num2), 1)
    text_similarity = SequenceMatcher(None, text1, text2).ratio()

    return  num_similarity

def identify_ocr_noise(original, recovered):
    diff = list(ndiff(original, recovered))
    noise_chars = []
    for i, char in enumerate(diff):
        if char.startswith('- ') or char.startswith('+ '):
            noise_chars.append((i, char))
    return noise_chars

def word_to_word_comparison(text1, text2):
    words1 = text1.split()
    #print(words1)
    words2 = text2.split()


    diff = list(ndiff(words1, words2))
    word_differences = [word for word in diff if word.startswith('- ') or word.startswith('+ ')]
    return word_differences
import re

def clean_word_differences(word_differences):
    cleaned_differences = [
        word for word in word_differences
        if not re.match(r"^[-+]\s*['.,]*$", word)  # Ignore punctuation-only changes
    ]
    return cleaned_differences


def character_mismatch_score(word1, word2):
    # Ensure both words are the same length by padding shorter word
    max_len = max(len(word1), len(word2))
    word1 = word1.ljust(max_len)  # Add spaces for alignment
    word2 = word2.ljust(max_len)

    #print(f'comparing {word1} with {word2}')
    
    score = 0
    for char1, char2 in zip(word1, word2):
        if char1 != char2:
            if char1.isalpha() and char2.isalpha():
                score += 1  # Alphabet-to-alphabet mismatch
            elif (char1 in string.punctuation or char2 in string.punctuation):
                score += 0.1  # Special character mismatch
            else:
                score += 0.1  # Alphabet to special character mismatch
    #print(score)            
    return score


def filter_noise_differences(word_differences):
    plus_words = []
    minus_words= []
    flagged_content = []
    word_score = 1

    for word in word_differences:
        # Ignore punctuation-only entries
        clean_word = word[2:].strip()  # Remove '+ ' or '- ' for checking
        if re.match(r"^[.,'\"!?]*$", clean_word):
            continue  # Skip punctuation-only words

        if word.startswith('+ '):
            #print(f'1st: {clean_word}')
            clean_word = word.translate(str.maketrans('', '', string.punctuation))
            plus_words.append(clean_word)
        elif word.startswith('- '):
            #print(f'2nd: {clean_word}')
            clean_word = word.translate(str.maketrans('', '', string.punctuation))
            minus_words.append(clean_word)

 # Ensure both lists are the same length before comparing
    for flt_word1, flt_word2 in zip(plus_words, minus_words):
        score = character_mismatch_score(flt_word1, flt_word2)
        if score >= 0.5:
            #print(f'Comparison between "{flt_word1}" and "{flt_word2}" - Score: {score}')
            flagged_content.append(f'Original:{flt_word1}')
            flagged_content.append(f'DOR:{flt_word2}')
            word_score = word_score-score

    print(f'Word Score{word_score}')
    return flagged_content, word_score
def authenticity_score(recoverd_image_path,decripted_orginial_file_path):
    if os.path.exists(recoverd_image_path):
        json_data_recovered = read_json_file(recoverd_image_path)
        text_values_recovered = extract_text_from_json(json_data_recovered)
        # print('Recovered')
        # print(text_values_recovered)
        json_data_original = read_json_file(decripted_orginial_file_path)
        text_values_original = extract_text_from_json(json_data_original)
        # print('Original')
        # print(text_values_original)

        char_count = sum(char.isalpha() for text in text_values_recovered for char in text)
        num_count = sum(char.isdigit() for text in text_values_recovered for char in text)
        total_characters = sum(len(text) for text in text_values_recovered)
        print(f"Recovered Total characters: {total_characters}")
        print(f"Recovered Character count: {char_count}")
        print(f"Recovered Number count: {num_count}")


        char_count = sum(char.isalpha() for text in text_values_original for char in text)
        num_count = sum(char.isdigit() for text in text_values_original for char in text)
        total_characters = sum(len(text) for text in text_values_original)
        print(f"Original Total characters: {total_characters}")
        print(f"Original Character count: {char_count}")
        print(f"Original Number count: {num_count}")

        #similarity = Levenshtein.ratio(text_values_original, text_values_recovered)  # Returns a value between 0 and 1
        #print(f"Similarity: {similarity:.2f}")

        text_values_original = str(text_values_original)
        #print(text_values_original)
        text_values_recovered = str(text_values_recovered)
        #print(text_values_recovered)
        similarity_score = weighted_similarity(text_values_original, text_values_recovered)
        number_differences = highlight_numbers(text_values_original, text_values_recovered)
        word_difference = word_to_word_comparison(text_values_original, text_values_recovered)
        cleaned_differences, word_score =filter_noise_differences(word_difference)

        print(f"Number Weighted Similarity Score: {similarity_score:.4f}")
        print(f"Number Differences: {number_differences}")
       # print(f"Word Differences: {word_difference}")
        print(f"Word Weighted Similarity Score: {word_score:.4f}")
        print(f"Word differences: {cleaned_differences}")

    else:
        print(f"File not found: {recoverd_image_path}")

    return similarity_score, word_score



# Example usage
if __name__ == "__main__":
    recoverd_image_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr\results.json'
    decripted_orginial_file_path = r'F:\papertrust\papertrust\results\surya\pdf_to_ocr_0_text_rev\results.json'
    similarity_score, word_score = authenticity_score(recoverd_image_path,decripted_orginial_file_path)





