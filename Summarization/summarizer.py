import cloudmersive_nlp_api_client
from cloudmersive_nlp_api_client.rest import ApiException
import torch
import pytextrank
import pandas as pd
from langdetect import detect
from Summarization.objectDetection.detector import image_detect


def adv_text_summary(text, model_t5, tokenizer_t5, APIKEY):
    summ = {}
    device = torch.device('cpu')
    # Detect language to know if translation is needed
    new_text = ""
    if detect(text) != 'en':
        # Use cloudmersive api call to translate
        configuration = cloudmersive_nlp_api_client.Configuration()
        # Go to https://www.cloudmersive.com/nlp-api and create your API key!
        configuration.api_key['Apikey'] = APIKEY
        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['Apikey'] = 'Bearer'

        # create an instance of the API class
        api_instance = cloudmersive_nlp_api_client.LanguageTranslationApi(
            cloudmersive_nlp_api_client.ApiClient(configuration))
        # Input translation request
        input = cloudmersive_nlp_api_client.LanguageTranslationRequest(text)

        try:
            # Translate French to English text with Deep Learning AI
            api_response = api_instance.language_translation_translate_fra_to_eng(input)
        except ApiException as e:
            print("Exception when calling LanguageTranslationApi->language_translation_translate_fra_to_eng: %s\n" % e)
        new_text = " ".join(api_response.translated_text_result)

    # Proceed to text summarization
    if new_text:
        new_t5_prepared_Text = "summarize: " + new_text
    else:
        new_t5_prepared_Text = "summarize: " + text
    tokenized_text = tokenizer_t5.encode(new_t5_prepared_Text, return_tensors="pt").to(device)

    # summmarize (same process, different instruction)
    summary_ids = model_t5.generate(tokenized_text,
                                 num_beams=4,
                                 no_repeat_ngram_size=2,
                                 min_length=30,
                                 max_length=100,
                                 early_stopping=True)

    output = tokenizer_t5.decode(summary_ids[0], skip_special_tokens=True)
    summ['summary'] = output

    return summ


def text_summary(text, model_en, model_fr):
    # Initialize dictionary to contain all the topics of the text considered
    summ = {}
    # Initialize TextRank (Graph based) algorithm for text semantic identification
    tr = pytextrank.TextRank()
    # Load `french and english pre-trained Spacy models
    nlp_en = model_en
    nlp_fr = model_fr
    try:
        # If english model has not been added to the nlp pipe, do it
        nlp_en.add_pipe(tr.PipelineComponent, name="textrank", last=True)
    except ValueError:
        pass
    try:
        # If French model has not been added to the nlp pipe, do it
        nlp_fr.add_pipe(tr.PipelineComponent, name="textrank", last=True)
    except ValueError:
        pass

    # Detect language to know which pipelining to choose
    if detect(text) == 'en':
        doc = nlp_en(text)
    # In my case if the language detected is not english it is most certainly French
    else:
        doc = nlp_fr(text)

    # Retrieve top 20 tags considered as most reflecting of the content of the text based on Spacy model
    tags = doc._.phrases[0:21]
    # Save in initialized dictionary
    summ["tags"] = tags

    return summ


def table_summary(table):
    # Initialize dictionary to contain characteristics of table considered
    summ = {}
    # Retrieve all data types found in table
    data_dtypes = pd.DataFrame(table.dtypes, columns=["type"])
    # Retrieve all column names found in table
    data_names = list(table.columns)
    # Count number of columns grouped by data type of that column and save as dictionary
    data_dtypes = data_dtypes.reset_index().groupby('type').count().reset_index().rename(
        columns={"index": "count"}).to_dict('records')
    # Create two layers for both summary information
    summ["column_names"] = data_names
    summ["column_types"] = data_dtypes

    return summ


def summarize(raw, file_type, model_en, model_fr, filepath, detector, t5, model_t5, tokenizer_t5, APIKEY):
    # General purpose function to summarize content of file considered base on file type
    summ = {}
    if file_type == 'txt':
        if t5:
            summ["text_contents"] = adv_text_summary(raw, model_t5, tokenizer_t5, APIKEY)
        else:
            summ["text_contents"] = text_summary(raw, model_en, model_fr)
    # In case the case of an image, we call the summarization function from the objectDetection sub folder
    elif file_type == 'img':
        summ["photo_subjects"] = image_detect(filepath, detector)
    elif file_type == "sheets":
        for k in raw.keys():
            summ[k] = table_summary(raw[k])
    elif file_type == "table":
        summ["table_contents"] = table_summary(raw)

    return summ
