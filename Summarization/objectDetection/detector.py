import os
from imageai.Detection import ObjectDetection
# Make sure computations are done on CPU (I don't have a GPU smh)
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Define path to model & garbage can for image output with detection boxes classification
model_path = os.getcwd() + "/Summarization/objectDetection/models/yolo-tiny.h5"
output_path = os.getcwd() + "/Summarization/objectDetection/output/newimage.jpg"


def image_detect(path, model=model_path):
    # Initialize dictionary to contain all elements the model has identified within the photo
    summ = {}
    # Initialize object detection instance
    detector = ObjectDetection()
    # Set model to be used as TinyYOLOv3 and load
    detector.setModelTypeAsTinyYOLOv3()
    detector.setModelPath(model)
    detector.loadModel()

    # Generate list of elements identified in photo
    detection = detector.detectObjectsFromImage(input_image=path, output_image_path=output_path)
    i = 0
    for eachItem in detection:
        # For each element identified, attribute it a key as the name of the element and value the percentage probaility
        # that it is that element
        summ[str("element " + str(i) + " " + str(eachItem["name"]))] = str(round(eachItem["percentage_probability"])) + "%"
        i += 1
    return summ
