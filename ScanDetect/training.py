from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.externals import joblib
import os
import cv2
import numpy as np
from skimage.feature import hog
from skimage.color import rgb2gray


Text_path = os.getcwd() + "/text_nontext-dataset/text"
Non_Text_path = os.getcwd() + "/text_nontext-dataset/nontext"
test_path = os.getcwd() + "/crossvalidation-set/text/"
Non_test_path = os.getcwd() + "/crossvalidation-set/non_text"

def preprocess(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(img, (40, 40))
    return image

def extractfeat(path):
    list_hog_fd = []
    for files in os.listdir(path):
        img = preprocess(path + "/" + files)
        print(path + "/" + files)
        fd = hog(img, orientations=9, pixels_per_cell=(30, 30), cells_per_block=(1, 1))
        list_hog_fd.append(fd)
    hog_features = np.array(list_hog_fd, 'float64')
    return hog_features

def train_test():
    print("Extracting Features(0%)")
    train_text = extractfeat(Text_path)
    print("Extracting Features(25%)")
    train_nontext = extractfeat(Non_Text_path)
    print("Extracting Features(50%)")
    test_text = extractfeat(test_path)
    print("Extracting Features(75%)")
    test_nontext = extractfeat(Non_test_path)
    print("Done")

    trainfeat = np.vstack((train_text, train_nontext))
    testfeat = np.vstack((test_text, test_nontext))

    trainfeat = preprocessing.normalize(trainfeat)
    testfeat = preprocessing.normalize(testfeat)

    print("Saving Features....")
    np.save("./trainfeat.mat", trainfeat)
    np.save("./testfeat.mat", testfeat)
    print("Saved")

    trainlabeltext = np.ones(len(os.listdir(Text_path)))
    trainlabelnontext = np.zeros(len(os.listdir(Non_Text_path)))
    labeltrain = np.hstack((trainlabeltext, trainlabelnontext))

    testlabeltext = np.ones(len(os.listdir(test_path)))
    testlabelnontext = np.zeros(len(os.listdir(Non_test_path)))
    labeltest = np.hstack((testlabeltext, testlabelnontext))

    svclassifier = SVC(kernel='rbf')
    svclassifier.fit(trainfeat, labeltrain)
    print("Training Model.....")
    y_pred_train = svclassifier.predict(trainfeat)
    y_pred_test = svclassifier.predict(testfeat)
    print("Done")
    print("Training:" + classification_report(labeltrain, y_pred_train))
    print("Testing:" + classification_report(labeltest, y_pred_test))

    joblib.dump(svclassifier, 'Model.pkl')

train_test()