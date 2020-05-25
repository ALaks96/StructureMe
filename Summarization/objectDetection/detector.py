import os
from imageai.Detection import ObjectDetection
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

model_path = os.getcwd() + "/Summarization/objectDetection/models/yolo-tiny.h5"
output_path = os.getcwd() + "/Summarization/objectDetection/output/newimage.jpg"


def image_detect(path, model=model_path):
    summ = {}
    detector = ObjectDetection()
    detector.setModelTypeAsTinyYOLOv3()
    detector.setModelPath(model)
    detector.loadModel()

    detection = detector.detectObjectsFromImage(input_image=path, output_image_path=output_path)
    i = 0
    for eachItem in detection:
        summ[str("element " + str(i) + " " + str(eachItem["name"]))] = str(round(eachItem["percentage_probability"])) + "%"
        i += 1
    return summ
