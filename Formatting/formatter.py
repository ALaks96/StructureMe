import os
import json
import pandas as pd
from datetime import datetime


def get_arbo(root):
    # General purpose function to walk through all dir/nested dirs contained within specified root. Will append to a
    # list of file paths a file location if the file type is handled by this program
    valid_ext = [
        "ppt", "pptx", "docx", "xlsx", "xls",
        "pdf",
        "txt",
        "csv", "tsv",
        "jpeg", "jpg", "png"
    ]
    paths = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith(tuple(valid_ext)):
                paths.append(os.path.join(path, name))
    return paths


def validateJSON(jsonData):
    # Json compatible python object checker/test function
    try:
        json.loads(jsonData)
    except ValueError:
        return False
    return True


class DateTimeEncoder(json.JSONEncoder):
    # JSON encoder to overwrite default encoder in case of incompatible datetime format
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def jsonKeys2int(x):
    # Function to convert json keys from string to integers for server-side querying easing
    if isinstance(x, dict):
        return {int(k): v for k, v in x.items()}
    return x


def to_json(dic, file_name="metadata.json"):
    # Function to save python object as a json
    js = json.dumps(dic, indent=1, default=str)

    # Open new json file if not exist it will create
    fp = open(os.getcwd() + "/" + str(file_name), 'w')

    # write to json file
    fp.write(js)

    # close the connection
    fp.close()


def dic_for_viz(final_dic):
    # Function to generate a dictionary that can be later process by other python methods (meant for visualization
    # purposes)
    collection = {}
    index = 1
    for doc, meta in final_dic.items():
        metadata = {}
        for key, value in final_dic[doc].items():
            if key != "Content":
                metadata[key] = value
        collection[index] = metadata
        index += 1

    return collection


def meta_to_df(final_dic, save=False):
    # Function to specifically convert metadata retrieved to csv for visualization purposes
    df = pd.DataFrame(dic_for_viz(final_dic))
    df = df.T
    if save:
        df.to_csv("Output/metadata.csv")

    return df
