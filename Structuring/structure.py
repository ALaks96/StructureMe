from __future__ import print_function
from Extraction.metadata_extractor import get_meta
from Extraction.content_extractor import get_content
from Formatting.formatter import get_arbo
from Formatting.formatter import to_json
from Summarization.summarizer import summarize


def structure_me(path, save=True, json_name="Output/scan.json", en=None, fr=None):
    print("#####################")
    print("SCAN STARTED")
    # Initiate mega dic containing everything
    megadic = {}
    index = 1

    # Get all file locations from root
    arbo = get_arbo(path)
    print(arbo)
    print("Got file locations")

    for file in arbo:
        print("-----------------------")
        print("Fetching : ", file)
        # Initiate same key dic to be completed every time
        # try:
        dic_of_files = {}

        # Get metadata of opord and assign it
        meta = get_meta(file)
        print("-----------------------")
        print("Got metadata")
        dic_of_files['title'] = meta['Title']
        dic_of_files['authors'] = meta['Author(s)']
        dic_of_files['last_modified_by'] = meta['Last Modified By']
        dic_of_files['created_date'] = meta['Created Date']
        dic_of_files['modified_date'] = meta['Modified Date']
        dic_of_files['location'] = file
        dic_of_files['content'], raw, file_type = get_content(file)
        # if file.endswith("pdf"):
        #     print(raw)
        print("-----------------------")
        print("Got content")
        dic_of_files['summary'] = summarize(raw, file_type, model_en=en, model_fr=fr)
        print("-----------------------")
        print("Got summary")
        # And assign all of this to our megadic, indexed by incremental numbers!
        megadic[int(index)] = dic_of_files
        print("-----------------------")
        print("Saved to final indexed data base")
        index += 1
        # except Exception as e:
        #     print("ERROR::", e, ':', os.path.basename(file))
    print("SCAN FINISHED")
    print("#####################")
    # for k,v in megadic.items():
    #     print(megadic[k]['summary'])

    if save:
        to_json(megadic, json_name)

    return megadic