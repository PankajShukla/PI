
import pandas as pd
import numpy as np
import re
import json

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import matplotlib.colors as mcolors

pd.set_option('display.max_columns',500)
pd.set_option('display.max_rows',50)

nltk.download('wordnet')
nltk.download('omw-1.4')
lemmatizer = WordNetLemmatizer()

nltk.download('stopwords')
nltk.download('punkt')
stop_words = list(set(stopwords.words('english')))

def lemmatize_text(text):
    words = text.split()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    lemmatized_text = ' '.join(lemmatized_words)
    return lemmatized_text


def get_unique_words(items_list):
    unique_words = set()
    
    for item in items_list:
        words = re.split(r'[ /]', item)
        unique_words.update(words)

    text_words_ = list(unique_words)

    text_words = []
    for t in text_words_:
        text_words.append(lemmatize_text(t))
    
    return text_words



def find_word_occurrences(word_list, text):
    word_occurrences = {}
    items_list = text.lower().split()

    unique_words = set()
    for item in items_list:
        words = re.split(r'[ /]', item)
        unique_words.update(words)  # Add each word to the set

    text_words_ = list(unique_words)

    text_words = []
    for t in text_words_:
        text_words.append(lemmatize_text(t))
    
    for word in word_list:
        word_lower = word.lower()
        word_occurrences[word] = text_words.count(word_lower)
    
    return word_occurrences




def find_word_combination_occurrences(items_list):

    word_combinations = []
    for item in items_list:
        word_comb = re.split(r'[,]', item)
        for wc in word_comb:
            wc = wc.strip()
            wc = wc.replace(".","")
            word_combinations.append(wc)

    word_combinations_lemma = []
    for wc in word_combinations:
        wc_lemma = lemmatize_text(wc)
        word_combinations_lemma.append(wc_lemma)
    
    return word_combinations_lemma


def apply_word_occurrences_to_df(row, text_column, word_list):
    row['word_occurrences'] = row[text_column].apply(lambda x: find_word_occurrences(word_list, x))
    return row



def find_first_match(word_list, text):

    items_list = text.lower().split()
    unique_words = set()
    for item in items_list:
        words = re.split(r'[ /]', item)
        unique_words.update(words)
        
    text_words_ = list(unique_words)

    text_words = []
    for t in text_words_:
        text_words.append(lemmatize_text(t))


    for word in text_words:
        if word in [w.lower() for w in word_list]:
            return word
    return 'unknown'
    

def apply_find_first_match_to_df(row, text_column, word_list):
    row['new_'+text_column] = row[text_column].apply(lambda x: find_first_match(word_list, x))
    return row


def remove_words_from_list(main_list, remove_list):
    filtered_list = [word for word in main_list if word not in remove_list]
    return filtered_list


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def shorten_list(input_list, max_distance):
    unique_words = []

    for word in input_list:
        # Check if the word is similar to any already stored unique words
        if not any(levenshtein_distance(word, unique_word) <= max_distance for unique_word in unique_words):
            unique_words.append(word)

    return unique_words


def extract_numeric_values_for_pricing(text):
    text = text.replace(",","")
    numeric_values = list(re.findall(r'\d+', text))
    if len(numeric_values)==2:
        return numeric_values
    else:
        value = [0,0]
        return value



def get_hex(color_name):

    colors = {
        "rose": "#FF007F", "dusty": "#D4A373", "nude": "#F2D3BC", "mauve": "#E0B0FF", "dark": "#1B1B1B", 
        "dark-red": "#8B0000", "light": "#F8F9FA", "light-blue": "#ADD8E6", "cream": "#FFFDD0", "light-gray": "#D3D3D3",
        "off-white": "#FAF9F6", "dark-blue": "#00008B", "leopard": "#A57C1B", "charcoal": "#36454F", "denim": "#1560BD",
        "wash": "#B6D0E2", "blush": "#DE5D83"
    }

    if color_name=='offwhite':
        color_name = 'off-white'

    default_HEX = '#39FF14'
    try:
        hex_value = mcolors.CSS4_COLORS[color_name]
        return str(hex_value)
    except:
        for c in list(colors.keys()):
            if color_name==c:
                return colors[c]
        
        return default_HEX



