# StructureMe

Created this program for my master thesis. 
The objective was to create a program that will scan all dirs/subdirs for text files, tables, images and structure these 
elements in JSON format to allow query with a server with a nice front-end visual representation / webapp.
Three main functions are offered by this program for a given file:

- Extract all content 
- Extract all metadata (at least what is available)
- Summarize content (which varies depending on file type)

For summarization the following three methods are considered: 
            
**TEXT:** Topic extraction for text files using Spacy/Nltk OR cloudmersive API (to translate French to English) + Google T5 model 

**IMAGE:** Object Detection for images using YOLO

**TABLE:** Brief characteristics for tables (column names, dtypes)
       
Once all functions are applied to each file this program supports (MSOffice files, PDF, Scanned PDF, JPG/PNG/JPEG, csv, 
tsv), it appends whatever it managed to extract in a dictionary which it will save in JSON format.

Depending on which files you want to structure, choose where you clone this repo accordingly. It will structure all 
files contained in the directory you pass as an argument. Another possibility is to drop files you wish to structure in 
the **Data** folder of the repo. 

# Running the program

```
cd StructureMe
source bin/activate
python3 -m pip install -r requirements.txt
python3 main.py /path/to/dir/you/want/to/structure/
```

Outputted JSON can be found in **Output** folder