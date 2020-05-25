import os
from imageai.Detection import ObjectDetection
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

model_path = os.getcwd() + "/Summarization/objectDetection/models/yolo-tiny.h5"
output_path = os.getcwd() + "/Summarization/objectDetection/output/newimage.jpg"


def image_detect(path):
    summ = {}
    contents = []
    detector = ObjectDetection()
    detector.setModelTypeAsTinyYOLOv3()
    detector.setModelPath(model_path)
    detector.loadModel()

    detection = detector.detectObjectsFromImage(input_image=path, input_type="array", output_image_path=output_path)

    for eachItem in detection:
        contents.append(str(eachItem["name"] + " : " + round(eachItem["percentage_probability"])) + "%")
    summ["contents"] = contents
    return summ
