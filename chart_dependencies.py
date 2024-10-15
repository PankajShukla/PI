
import pandas as pd
import numpy as np
import re
import json

from utility import *


def get_frequency(df_, col):

    df_[col] = df_[col].str.lower()
    df_[col] = df_[col].str.replace('"','').str.replace("'",'')
    df_[col] = df_[col].str.replace(")",'').str.replace("(",'').str.replace("-",'')
    df_[col] = df_[col].str.strip()

    unique_words = get_unique_words(df_[col].unique())
    word_list = unique_words
    # word_list = remove_words_from_list(word_list, stop_words)
    
    df_WF = apply_word_occurrences_to_df(df_, col, word_list)
    df_WF = pd.DataFrame(df_WF['word_occurrences'].tolist())
    
    WF = pd.DataFrame(df_WF[word_list].sum()).reset_index()
    WF.columns=[col, 'word_freq']
    WF = WF.sort_values('word_freq', ascending=False)
    return WF



def get_word_combination_frequency(df_, col, _brand):

    brandfield = 'Brand_D2C'
    df_ = df_[df_[brandfield]== _brand]
    df_[col] = df_[col].str.lower()
    df_[col] = df_[col].str.strip()

    items_list = df_[col].to_list()
    text_word_combination = find_word_combination_occurrences(items_list)

    word_list = list(set(text_word_combination))

    word_occurrences = {}
    for word in word_list:
        word_occurrences[word] = text_word_combination.count(word)
    
    WF = pd.DataFrame(list(word_occurrences.items()), columns=[col, 'word_freq'])
    WF = WF.sort_values('word_freq', ascending=False)
    
    WF = WF[WF[col]!='-']
    
    WF = WF.head(6)
    WF = WF.reset_index()
    WF.drop(columns='index', inplace=True)
    WF['word_freq_perc'] = round((WF['word_freq']/WF['word_freq'].sum())*100,0)
    
    WF[brandfield] = _brand
    WF['distribution'] = WF[col] + " : " + WF['word_freq_perc'].astype('str')+"%"
    
    WF = WF.groupby([brandfield]).agg(
        distribution = ('distribution', list)
    ).reset_index()
    WF.rename(columns={'distribution':col}, inplace=True)
    
    return WF



def color_frequency_brand(df_, col, _brandList):

    df_Dict = {}
    
    for b in _brandList:
        df_temp = df_[(df_['Brand_D2C']==b)]
        df_temp = get_frequency(df_temp, col)
        df_temp = df_temp.reset_index()
        df_temp.drop(columns='index', inplace=True)
        df_temp['color_HEX'] = df_temp[col].apply(lambda x: get_hex(x))
        df_temp =  df_temp[df_temp['word_freq']>= 0.02* int(df_temp['word_freq'].sum())]
    
        df_Dict[b] = df_temp
        
    return df_Dict


def color_frequency(df_, col):
    
    df_temp = get_frequency(df_, col)
    df_temp = df_temp.reset_index()
    df_temp.drop(columns='index', inplace=True)
    df_temp['color_HEX'] = df_temp[col].apply(lambda x: get_hex(x))
    df_temp =  df_temp[df_temp['word_freq']>= 0.02* int(df_temp['word_freq'].sum())]
        
    return df_temp



def pricing_frequency(df_, _brandList, col):

    df_Dict = {}

    i = 0
    values = [None]*len(_brandList)
    
    for b in _brandList:
        df_temp = df_[df_['Brand_D2C']==b][[col]]
        values[i] = df_temp['Price_Tentative']
        df_Dict[b] = df_temp
        i=i+1
        
    return df_Dict, values

