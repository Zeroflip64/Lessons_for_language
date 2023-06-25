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

@st.cache_data()

def ss_features_fill_mask_data():
  class SentenceSimilarity:
      def __init__(self, model_name='distilbert-base-uncased'):
          self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
          self.model = DistilBertModel.from_pretrained(model_name)

      def sentence_to_vec(self, sentence: str):
          inputs = self.tokenizer(sentence, return_tensors="pt")
          outputs = self.model(**inputs)
          return outputs.last_hidden_state.mean(dim=1).detach().numpy().squeeze()

      def compare_sentences(self, sentence1: str, sentence2: str):
          vec1 = self.sentence_to_vec(sentence1)
          vec2 = self.sentence_to_vec(sentence2)
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



  fill_mask = pipeline(
      "fill-mask",
      model="distilbert-base-multilingual-cased",
      tokenizer="distilbert-base-multilingual-cased"
  )
  syb_all=pd.read_csv('https://raw.githubusercontent.com/Zeroflip64/Lessons_for_language/blob/main/sub_all.csv')


  

  return SentenceSimilarity,Features,fill_mask,syb_all
  
SentenceSimilarity,Features,fill_mask,syb_all=ss_features_fill_mask_data()

document=None
uploaded_file = st.file_uploader("Загрузите ваш документ", type=["txt"])

if uploaded_file is not None:
    document = uploaded_file.read().decode('utf-8')
    st.text(document)


clean=Features(document)
df=clean.sentences
ss=SentenceSimilarity()

def empty_words(df):
  type_of_words={'глагол':'VERB','сущ':'NOUN','прил':'PRON'}
  tape=input('Выбирите тип слова и впешити (глагол , сущ , прил) ')
  text=None
  count=0

  while count!=1:
    sentenses=random.choice(df)
    text=nlp(sentenses)

    if type_of_words[tape] in [i.pos_ for i in text] and len(text.text)>10:
      count+=1
      text=text



  pos=[i[0] for i in enumerate(text)if i[-1].pos_==type_of_words[tape]]# ИНДЕКС
  random_choise=random.choice(pos)
  new_text=[i.text for i in text]
  word=new_text[random_choise]
  new_text[random_choise]='[MASK]'# Создали пропуск
  sentenses_with_empty=' '.join(new_text)


  senten = [sentenses_with_empty]
  variants = []
  for sentence in senten:
      predictions = fill_mask(sentence, top_k=3)
      for i, pred in enumerate(predictions):
        if pred['token_str'] != word:
          variants.append(pred['token_str'])
  variants.append(word)

  sentences=sentenses_with_empty.replace('[MASK]','_________')
  print(f"Выбери верное слово в предложении {sentences}")
  print(f'Варианты слов {variants}')
  if input()==word:
    print('Поздравляем вы выбрали верное слово')
  else:
    print(f'Вы ошиблись, верное слово {word}')

empty_words(df)
