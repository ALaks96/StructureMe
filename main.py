import os
from Structuring.structure import structure_me
import spacy

try:
    nlp_fr = spacy.load('fr_core_news_sm')
except OSError:
    print("run this in your terminal: python -m spacy download fr_core_news_sm")

try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    print("run this in your terminal: python -m spacy download en_core_web_sm")

root = os.getcwd() + "/Data/"
structure_me(root, en=nlp_en, fr=nlp_fr)