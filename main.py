import os
import sys
import spacy
from Structuring.structure import structure_me
from imageai.Detection import ObjectDetection

# Start by loading nlp models in en & fr, catch exception if model is not downloaded
try:
    nlp_fr = spacy.load('fr_core_news_sm')
except OSError:
    print("run this in your terminal: python -m spacy download fr_core_news_sm")

try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    print("run this in your terminal: python -m spacy download en_core_web_sm")

# Set path to object detection model
model_path = os.getcwd() + "/Summarization/objectDetection/models/yolo-tiny.h5"
# Initialize object detection instance with exception handling in case model is not downloaded
try:
    detector = ObjectDetection()
    # Set model to be used as TinyYOLOv3 and load
    detector.setModelTypeAsTinyYOLOv3()
    detector.setModelPath(model_path)
    detector.loadModel()
except Exception as e:
    print(e)
    print("You need to download a model for object detection such as TinyYOLOV3")

# check if user has passed a location as parameter, otherwise fetch in Data folder
try:
    if sys.argv[1]:
        root = sys.argv[1]
    else:
        # Define root as location where program is installed
        root = os.getcwd() + "/Data/"
except IndexError:
    root = os.getcwd() + "/Data/"
# Launch program
structure_me(root, en=nlp_en, fr=nlp_fr, model_detector=detector)