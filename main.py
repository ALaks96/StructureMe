import os
import sys
import spacy
from Structuring.structure import structure_me
from imageai.Detection import ObjectDetection
from transformers import T5Tokenizer, T5ForConditionalGeneration


# Start by loading nlp models in en & fr, catch exception if model is not downloaded
nlp_fr = None
nlp_en = None
t5 = None
model_t5 = None
tokenizer_t5 = None

if len(sys.argv) == 1:
    try:
        nlp_fr = spacy.load('fr_core_news_sm')
    except OSError:
        print("run this in your terminal: python -m spacy download fr_core_news_sm")

    try:
        nlp_en = spacy.load("en_core_web_sm")
    except OSError:
        print("run this in your terminal: python -m spacy download en_core_web_sm")

else:
    t5 = sys.argv[1]
    ans = input('Have you been to https://www.cloudmersive.com/nlp-api to create your API key? yes/no answers only')
    if ans == "yes":
        API_KEY = input("Please enter your API key here:")
    else:
        t5 = None
        print("If you want to use T5 you need to get an API key, visit https://www.cloudmersive.com/nlp-api to create"
              "one, it's free! Using Spacy models and graph approach instead.")
        try:
            nlp_fr = spacy.load('fr_core_news_sm')
        except OSError:
            print("run this in your terminal: python -m spacy download fr_core_news_sm")

        try:
            nlp_en = spacy.load("en_core_web_sm")
        except OSError:
            print("run this in your terminal: python -m spacy download en_core_web_sm")
    model_t5 = T5ForConditionalGeneration.from_pretrained('t5-small')
    tokenizer_t5 = T5Tokenizer.from_pretrained('t5-small')

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
# try:
#     if sys.argv[1]:
#         root = sys.argv[1]
#     else:
#         # Define root as location where program is installed
#         root = os.getcwd() + "/Data/"
# except IndexError:
root = os.getcwd() + "/Data/"
# Launch program
structure_me(root, en=nlp_en, fr=nlp_fr, model_detector=detector, inp_t5=t5, inp_model_t5=model_t5,
             inp_tokenizer_t5=tokenizer_t5, API_KEY=None)