import os
from Extraction.metadata_extractor import get_meta
from Extraction.content_extractor import get_content
from Formatting.formatter import get_arbo
from Formatting.formatter import to_json
from Summarization.summarizer import summarize


def structure_me(path, save=True, json_name="Output/scan.json", en=None, fr=None, model_detector=None):
    # Function which calls all other functionalities to extract all necessary data from each file
    print("#####################")
    print("SCAN STARTED")
    # Initiate mega dictionary containing everything
    megadic = {}
    # Initiate index for file number (for server side query easing)
    index = 1

    # Get all file locations from root
    arbo = get_arbo(path)
    print(arbo)
    print("Got file locations")

    for file in arbo:
        # For each file contained within the list of valid file paths (depending on their file type)
        print("-----------------------")
        print("Fetching : ", file)
        try:
            # Initiate same key dic to be completed every time with metadata keys, content key, summary key
            dic_of_files = {}

            # Get metadata of file, get_meta() will call appropriate function depending on the extension given
            meta = get_meta(file)
            print("-----------------------")
            print("Got metadata")
            # Generate metadata layer containing all necessary keys (parallel to content and summary)
            dic_of_files['title'] = meta['Title']
            dic_of_files['authors'] = meta['Author(s)']
            dic_of_files['last_modified_by'] = meta['Last Modified By']
            dic_of_files['created_date'] = meta['Created Date']
            dic_of_files['modified_date'] = meta['Modified Date']
            dic_of_files['location'] = file

            # Call get_content() function which will use appropriate method to extract content from file depending on
            # its type
            dic_of_files['content'], raw, file_type = get_content(file)
            print("-----------------------")
            print("Got content")
            # Call summarize() function which will apply appropriate method to summarize the content retrieved above.
            # We pass the different models as parameters to avoid loading them every time
            dic_of_files['summary'] = summarize(raw, file_type, model_en=en, model_fr=fr, filepath=file,
                                                detector=model_detector)
            print("-----------------------")
            print("Got summary")
            # And assign all of this to our mega dictionary indexed by incremental numbers!
            megadic[int(index)] = dic_of_files
            print("-----------------------")
            print("Saved to final indexed data base")
            index += 1
        # If error occurs, highlight the filepath to control in Troubleshooting folder containing notebook for trouble
        # shooting
        except Exception as e:
            print("ERROR::", e, ':', os.path.basename(file))
    print("SCAN FINISHED")
    print("#####################")
    # for k,v in megadic.items():
    #     print(megadic[k]['summary'])

    # Once the program has parsed content, metadata and summarized every valid file it has scanned from root, save it
    # in JSON format to be compatible with server side querying
    if save:
        to_json(megadic, json_name)

    return megadic
