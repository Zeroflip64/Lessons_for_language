# -*- coding: utf-8 -*-
"""Untitled39.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vY1cWaAgdC6oEjsRZVuAYBRefxM2PFqw
"""

import pandas as pd
import numpy as np
import nltk
nltk.download('punkt')
nltk.download('cmudict')
nltk.download('stopwords')
nltk.download('reuters')
nltk.download('words')
import spacy
import pysrt
import datetime
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import cmudict, stopwords, reuters, words as nltk_words
from nltk.probability import FreqDist
from nltk import ngrams
from textstat import textstat
import re
from transformers import DistilBertModel, DistilBertTokenizer
import torch
from scipy.spatial.distance import cosine
import random
from textstat import flesch_kincaid_grade, gunning_fog, smog_index
import torch
from pyinflect import getInflection
from transformers import pipeline
from spellchecker import SpellChecker
import en_core_web_sm
import streamlit as st
nlp=spacy.load('en_core_web_sm')


@st.cache_resource
def init_model(model_name='distilbert-base-uncased'):
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertModel.from_pretrained(model_name)
    return tokenizer, model

def sentence_to_vec(sentence, tokenizer, model):
    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy().squeeze()

def compare_sentences(sentence1, sentence2, tokenizer, model):
    vec1 = sentence_to_vec(sentence1, tokenizer, model)
    vec2 = sentence_to_vec(sentence2, tokenizer, model)
    similarity = 1 - cosine(vec1, vec2)
    return similarity
    
@st.cache_data()
def verb_time(words):  # Функция времени глагола
  inflection_tags = ['VBD', 'VBZ', 'VBG']
  timed_words = []
  for tag in inflection_tags:
    inflections = getInflection(words, tag=tag)
    for inflection in inflections:
        timed_words.append(inflection)
  return timed_words
    
@st.cache_data()
def correct_spelling(word):
    spell = SpellChecker(language='en')
    corrected_word = spell.correction(word)
    return corrected_word
    
@st.cache_data()
def to_base_form(word):# выводит в начальную форму слова
    if word is None:
        return None
    token = nlp(word)[0]
    base_form = token.lemma_
    return base_form
    
@st.cache_resource
def load_fill_mask_pipeline():
    return pipeline(
        "fill-mask",
        model="distilbert-base-multilingual-cased",
        tokenizer="distilbert-base-multilingual-cased"
    )
    
class Features:
  d = cmudict.dict()
  word_freqs = FreqDist(i.lower() for i in reuters.words())
  common_words = set(nltk_words.words())
  stop_words = set(stopwords.words('english'))
  nlp=spacy.load('en_core_web_sm')
    
  def __init__(self, first):
      self.first = first
      self.clean_text = self.clean_html(self.first)
      self.sentences = sent_tokenize(self.clean_text)
      words = word_tokenize(self.clean_text)
      self.words = [word.lower() for word in words if word.isalpha()]
      self.non_stopwords = [word for word in self.words if word not in self.stop_words]
      self.complex_words = self.hard_words()
      self.doc = self.nlp(self.first)

  def clean_html(self, raw_html):
      cleanr = re.compile('<.*?>')
      intermediate_text = re.sub(cleanr, '', raw_html)
      cleantext = intermediate_text.replace('\n', ' ')
      return cleantext

  def nsyl(self, word):#слоги
      return max([len(list(y for y in x if y[-1].isdigit())) for x in self.d.get(word.lower(), [])] or [0])

  def hard_words(self, frequency_threshold=5000):# сложные слова которые встречаются в тексте
      return {
          word for word in self.non_stopwords if len(word) > 2 and word in self.d and self.nsyl(word) > 2 and self.word_freqs[word] < frequency_threshold
      }

  def gunning_fog(self):# Gunning Fog index
        total_sentences = len(self.sentences)
        total_words = len(self.words)
        complex_word_count = len(self.complex_words)
        
        
        if total_words and total_sentences:
            GF_index = 0.4 * ((total_words / total_sentences) + 100 * (complex_word_count / total_words))
            return GF_index
        else:
            return 0
          
url = 'https://raw.githubusercontent.com/Zeroflip64/Lessons_for_language/main/sub_all.csv'
syb_all = pd.read_csv(url)
syb_all=syb_all.set_index('EN',drop=True)

tokenizer, model = init_model()
fill_mask = load_fill_mask_pipeline()

document = None
uploaded_file = st.file_uploader("Загрузите ваш документ", type=["txt"])  

if uploaded_file is not None:
    document = uploaded_file.read()

    # make sure document is a string
    if isinstance(document, bytes):
        document = document.decode('utf-8')

if document is not None:
    clean = Features(document)
    df=clean.sentences
    hard_words=clean.hard_words()    
    st.write('Сложность вашего текста {clean.gunning_fog()}

    def empty_words(df):# Упражение 1
        type_of_words = {'глагол':'VERB', 'сущ':'NOUN', 'прил':'PRON'}
    
        tape = st.selectbox('Выбирите тип слова', ('глагол', 'сущ', 'прил'))
    
        if "correct_word" not in st.session_state:
            st.session_state.correct_word = ""
            
        if "sentence_with_blank" not in st.session_state:
            st.session_state.sentence_with_blank = ""
            
        if "variants" not in st.session_state:
            st.session_state.variants = []
    
        if st.button("Сгенерировать новое предложение."):
            word_type = type_of_words[tape]
            sentence = None
    
            while True:
                sentence = random.choice(df)
                text = nlp(sentence)
    
                if word_type in {i.pos_ for i in text} and len(text.text) > 10:
                    break
    
            indices = [i for i, token in enumerate(text) if token.pos_ == word_type]
            random_index = random.choice(indices)
    
            tokens = [token.text for token in text]
            st.session_state.correct_word = tokens[random_index]
            tokens[random_index] = '[MASK]'
            sentence_with_blank = ' '.join(tokens)
    
            predictions = fill_mask(sentence_with_blank, top_k=4)
            variants = set(pred['token_str'] for pred in predictions)
    
            # Ensure the correct answer is always an option
            variants.add(st.session_state.correct_word)
    
            st.session_state.variants = list(variants)
            random.shuffle(st.session_state.variants)
    
            st.session_state.sentence_with_blank = sentence_with_blank.replace('[MASK]', '_________')
    
        st.write(f"Выбери верное слово в предложении {st.session_state.sentence_with_blank}")
        st.write(f'Варианты слов {st.session_state.variants}')
    
        user_guess = st.text_input("Ваш ответ:")
    
        if st.button("Проверить ответ"):
            if user_guess:
                if user_guess == st.session_state.correct_word:
                    st.write('Поздравляем вы выбрали верное слово')
                else:
                    st.write(f'Вы ошиблись, верное слово {st.session_state.correct_word}') 

    
    def sentenses_by_time(sentenses_list):  # Пропуски на правильное время глагола
    
      if st.button('Выбрать новое предложение') or 'selected_sentence' not in st.session_state:
        st.session_state.selected_sentence = random.choice([sent for sent in sentenses_list if len(sent.split(' ')) > 5])
      
      doc = nlp(st.session_state.selected_sentence)
      sen = []
      verbs_indices = []
      verb_options = []
      correct_verbs = []
    
      for token in doc:
        if token.pos_ == 'VERB':
          sen.append('_______')
          verbs_indices.append(len(sen) - 1)
          options = verb_time(token.lemma_)
          options.append(str(token))  # Add the original verb to options
          verb_options.append(options)
          correct_verbs.append(str(token))
        else:
          sen.append(token)
    
      st.write(f"Выберите верное время глаголов в предложении   {' '.join([str(token) if isinstance(token, str) else token.text for token in sen])}")
    
      user_verbs = []
      for idx, options in enumerate(verb_options):
        user_verb = st.selectbox(f'Выберите время глагола для пропуска {idx+1}', options, key=f'verb{idx}')
        user_verbs.append(user_verb)
    
      if st.button('Проверить выбор'):
        mistakes = 0
        for idx, (user_verb, correct_verb) in enumerate(zip(user_verbs, correct_verbs)):
          if user_verb != correct_verb:
            st.write(f'Ошибка верное слово {correct_verb} для пропуска {idx+1}')
            mistakes += 1
        if mistakes:
          st.write('Попробуйте снова')
        else:
          st.write('Вы отлично справились')
    
        st.write(f'Количество ошибок {mistakes} из {len(user_verbs)} вариантов')
    
    def translate_book(word, purpose):#функция работы со словами
    
      words = []
      translates = []
      
      for i in word:
        try:
          translates.append(syb_all.loc[i][0])
          words.append(i)
        except:
          pass
    
      if purpose=='translate_book':
        help_words = pd.DataFrame({'ENG':words,'RUS':translates})
        return help_words
      elif purpose == 'exesises':
        book = dict(zip(words, translates))
    
        if st.button('Выбрать новое слово', key='new_word_button'):
          st.session_state.reset = True
    
        if 'reset' not in st.session_state or st.session_state.reset:
          st.session_state.selected_word = random.choice(list(book.keys()))
          st.session_state.reset = False 
    
        selected_word = st.session_state.selected_word
        word_translation = book[selected_word]
    
        shuffled_word = list(selected_word)  
        random.shuffle(shuffled_word)
    
        st.write(f'Соберите слово {word_translation}')
        st.write(f'Буквы {shuffled_word}')
    
        user_input = st.text_input('Ваш ответ')
    
        if st.button('Проверить ответ', key='check_answer_button'):
          if user_input:
            if user_input == selected_word:
              st.write('Все верно')
            else:
              st.write('Неверно, правильный ответ:', selected_word)
                
    def separate_by_meaning(sentence_list):
    
        type_of_words = ['VERB', 'NOUN', 'PRON', 'ADJ']
        names = []
        new_sentences = []
    
        if st.button('Получить предложение', key='new_sentence_10'):
            st.session_state.reset = True
    
        if 'reset' not in st.session_state or st.session_state.reset:
    
            while True:
                st.session_state.selected_sentence = random.choice(df)
                if len(st.session_state.selected_sentence.split()) > 4:
                    break
            st.session_state.reset = False  
    
        sentence = st.session_state.selected_sentence
    
        # Преобразование предложения в нормальную форму и исправление орфографии
        clean_sentences = nlp(' '.join([to_base_form(correct_spelling(i)).lower() if to_base_form(correct_spelling(i)) is not None else '' for i in sentence.split(' ')]))
    
        y = nlp(sentence)
    
        for token in y:
            if token.text.istitle() and token.text not in ['Little', 'Red', 'Cap']:
                names.append(token.text.lower())
    
        for i in clean_sentences:
            try:
                if i.pos_ in type_of_words and i.text not in names:
                    new_sentences.append(syb_all.loc[i.text][0])
                else:
                    new_sentences.append(i.text)
            except Exception as e:
                st.write(f"An error occurred: {e}")
                new_sentences.append(i.text)
    
        st.write('Заменить руские слова на английские ')
        new_sentences = ' '.join([token if isinstance(token, str) else token.text for token in new_sentences])
        st.write(new_sentences)
    
        user_sentences = st.text_input('Введите ваше предложение')
    
        if st.button('Проверить ответ', key='check_answer_button_10'):
            result = compare_sentences(sentence, user_sentences,tokenizer, model)
            st.write(f'Ваш текст совпал по смыслу на столько {np.round(result,1)*100} %')
    
    
    def split_of_sentences(df):
        if st.button('Получить предложение', key='new_sentence_15'):
            st.session_state.reset = True
    
        if 'reset' not in st.session_state or st.session_state.reset:
    
            while True:
                st.session_state.selected_sentence = random.choice(df)
                words = st.session_state.selected_sentence.split()
                if 2 < len(words) < 8:
                    break
            st.session_state.reset = False  
    
        sentence = st.session_state.selected_sentence
    
        if 'selected_sentence' in st.session_state and st.session_state.selected_sentence:
    
            words = sentence.split()
            random.shuffle(words)
            st.session_state.selected_words = words
            st.session_state.user_sentence = ""
    
            st.write(f'Составьте предложение из следующих слов: {st.session_state.selected_words}')
    
            user_sentence = st.text_input('Введите ваше предложение', value=st.session_state.user_sentence,key='choosing')
    
            if st.button('Проверить предложение',key='button_of_ok'):
                st.write(f"Предложения совпали c точностью {np.round(compare_sentences(sentence, user_sentence,tokenizer, model),1)*100}.")
    
    st.header('Словарь')
    st.subheader('В вашем тексте есть сложные слова ,постарайтесь выучить их')
    
    translate_b=translate_book(hard_words,'translate_book')
    st.write(translate_b)
    
    
    
    st.header('Упражнение 1')
    st.subheader('Упражнение где необходимо выбрать правильное слово подходящее по смыслу')
    st.text('1)Выберите часть речи')
    st.text('2)Нажмите кнопку по генерации предложения')
    st.text('3)Выберите слово и нажмите Enter')
    st.text('4)Нажмите кнопку на проверку вашего слова')
    empty_words(df)
    
    st.header('Упражнение 2')
    st.subheader('Упражение где необходимо выбрать правильное время у глагола исходя из смысла предложения')
    st.text('Нажмите кпоку для выбора предложения')
    st.text('Выберите слова из списка')
    st.text('Нажмите кнопку и получите количество верных ответов')
    sentenses_by_time(df)
    
    st.header('Упражнение 3')
    st.subheader('Необходимо из букв составить слово')
    translate_book(hard_words,'exesises')
    
    
    st.header('Упражнение 4')
    st.subheader('Дано предложение замените расские слова на английские и перепешите предложение')
    st.text('Нажмите кнопку получить предложение')
    st.text('Слова требующие перевода находяться в границах |_____|')
    st.text('Введите ваше предложение и нажмите Enter')
    st.text('Нажмите кнопку узнать результат')
    separate_by_meaning(df)
    st.text('Если ваш результат выше 85% то результат хороший поздравляем.')
    
    st.header('Упражнение 5')
    st.subheader('Необходимо из слов записать предложение')
    st.text('Нажмите кнопку получить предложение')
    st.text('Из полученных слов запишите предложение и нажмите Enter')
    st.text('Нажмите кнопку подтверждения')
    split_of_sentences(df)
    st.text('Если ваш результат выше 90% поздравляю')
     

    



