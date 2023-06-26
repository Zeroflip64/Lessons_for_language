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


@st.cache_data()
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


class Features:
  d = cmudict.dict()
  word_freqs = FreqDist(i.lower() for i in reuters.words())
  common_words = set(nltk_words.words())
  stop_words = set(stopwords.words('english'))
  nlp = spacy.load('en_core_web_sm')

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

  def flesch_kincaid(self):# Flesch-Kincaid grade level
      total_sentences = len(self.sentences)
      total_words = len(self.words)
      total_syllables = sum([self.nsyl(word) for word in self.words])


      if total_words and total_sentences:
          FK_grade = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
          return FK_grade
      else:
          return 0


@st.cache_data()
def load_fill_mask_pipeline():
    return pipeline(
        "fill-mask",
        model="distilbert-base-multilingual-cased",
        tokenizer="distilbert-base-multilingual-cased"
    )


fill_mask = load_fill_mask_pipeline()
url = 'https://raw.githubusercontent.com/Zeroflip64/Lessons_for_language/main/sub_all.csv'
syb_all = pd.read_csv(url)

  
tokenizer, model = init_model()


document=None
uploaded_file = st.file_uploader("Загрузите ваш документ", type=["txt"])

if uploaded_file is not None:
    document = uploaded_file.read().decode('utf-8')
    


clean=Features(document)
df=clean.sentences
st.write(df)

  if st.text_input()==word:
    st.write('Поздравляем вы выбрали верное слово')
  else:
    st.write(f'Вы ошиблись, верное слово {word}')

empty_words(df)
