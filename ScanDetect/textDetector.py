import cv2
import numpy as np
from skimage.feature import hog
from sklearn.externals import joblib
import os

clf = joblib.load('Model.pkl')

def preprocess(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(img, (40, 40))
    return image


def extractfeat(path):
    img = preprocess(path)
    fd = hog(img, orientations=9, pixels_per_cell=(30, 30), cells_per_block=(1, 1))
    hog_features = np.array(fd, 'float64')
    return hog_features


def text_or_not(path):
    img = extractfeat(path).reshape(1, 9)


    y_pred_test = clf.predict(img)
    print(y_pred_test)


text_or_not(os.getcwd() + "/Attestation sur l'honneur.jpeg")