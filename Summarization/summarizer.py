import pandas as pd
import pytextrank
from langdetect import detect
from Summarization.objectDetection.detector import image_detect


def text_summary(text, model_en, model_fr):
    tr = pytextrank.TextRank()
    nlp_en = model_en
    nlp_fr = model_fr
    try:
        nlp_en.add_pipe(tr.PipelineComponent, name="textrank", last=True)
    except ValueError:
        pass
    try:
        nlp_fr.add_pipe(tr.PipelineComponent, name="textrank", last=True)
    except ValueError:
        pass

    if detect(text) == 'en':
        doc = nlp_en(text)
    else:
        doc = nlp_fr(text)

    tags = doc._.phrases[0:21]

    return dict(tags)


def table_summary(table):
    summ = {}
    data_dtypes = pd.DataFrame(table.dtypes, columns=["type"])
    data_names = list(table.columns)
    data_dtypes = data_dtypes.reset_index().groupby('type').count().reset_index().rename(
        columns={"index": "count"}).to_dict('records')
    summ["column_names"] = data_names
    summ["column_types"] = data_dtypes

    return summ


def summarize(raw, file_type, model_en, model_fr):
    if file_type == 'txt':
        summ = text_summary(raw, model_en, model_fr)
    elif file_type == "table":
        summ = table_summary(raw)
    elif file_type == 'img':
        summ = {}
        summ["photo_subject"] = image_detect(raw)
    else:
        summ = []
        for k in raw.keys():
            print(k)
            summ.append(table_summary(raw[k]))

    return summ