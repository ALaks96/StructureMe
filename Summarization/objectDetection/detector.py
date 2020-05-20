from imageai.Detection import ObjectDetection

model_path = "./models/yolo-tiny.h5"
input_path = "./input/test45.jpg"
output_path = "./output/newimage.jpg"


def image_detect(path):
    contents = []
    detector = ObjectDetection()
    detector.setModelTypeAsTinyYOLOv3()
    detector.setModelPath(model_path)
    detector.loadModel()

    detection = detector.detectObjectsFromImage(input_image=path, output_image_path=output_path)

    for eachItem in detection:
        contents.append(str(eachItem["name"] + " : " + round(eachItem["percentage_probability"])) + "%")

    return contents
