import re
import os
import cv2
import zipfile
import pytesseract
import numpy as np
import pandas as pd
from PIL import Image

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
from io import StringIO
from pptx import Presentation
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdf2image import convert_from_path
from pytesseract import image_to_string
from Preprocessing.beautify import fix_text
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'


def docx_extractor(path, vectors=False):
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)
    doc = {}
    s = ''
    # vector = {}
    paragraph_nb = 1
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            text = ''.join(texts)
            doc[str(paragraph_nb)] = fix_text(text)
            s += fix_text(text)
#            if vectors:
#                vector[str(paragraph_nb)] = vectorizer(text, lang=detect(text))
#            else:
#                pass
            paragraph_nb += 1

#    if vectors:
#        return creator, doc, vector
    else:
        return doc, s


def ppt_extractor(path):
    paragraph_repo = {}
    # vector = {}
    f = open(path, "rb")
    prs = Presentation(f)
    slide_nb = 0
    s = ''
    for slide in prs.slides:

        slide_nb += 1
        temp_text = ''

        for shape in slide.shapes:

            if hasattr(shape, "text") and shape.text.strip():
                temp_text += shape.text

        paragraph_repo[str(slide_nb)] = fix_text(temp_text)
        s += fix_text(temp_text)
        # if vectors:
        #     vector[str(slide_nb)] = vectorizer(temp_text, lang=detect(text))
        # else:
        #     pass

    # if vectors:
    #     return creator, paragraph_repo, vector
    # else:
    return paragraph_repo, s


def txt_extractor(path):
    doc = {}
    # vector = {}
    paragraph_nb = 1
    s = ""

    with open(path) as f:
        lines = f.read()

    texts = lines.strip().split("/n/n")
    for text in texts:
        doc[str(paragraph_nb)] = fix_text(text)
        s += fix_text(text)
        # if vectors:
        #     vector[str(paragraph_nb)] = vectorizer(text, lang=detect(text))
        # else:
        paragraph_nb += 1

    # if vectors:
    #     return doc, vector
    # else:
    return doc, s


def pdf_extractor(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    current_page_number = 1
    paragraph_repo = {}
    # vector = {}
    s = ''

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        text = ''
        interpreter.process_page(page)

        text = retstr.getvalue()
        retstr.truncate(0)
        text = re.sub(u'(\u0000)', "", text)
        paragraph_repo[str(current_page_number)] = fix_text(text)
        s += fix_text(text)
        # if vectors:
        #     vector[str(current_page_number)] = vectorizer(text, lang=detect(text))
        # else:
        #     pass
        current_page_number += 1

    fp.close()
    device.close()
    retstr.close()
    # if vectors:
    #     return Classified, creator, paragraph_repo, vector
    # else:
    return paragraph_repo, s


def img_extractor(path):
    dic = {}
    img = cv2.imread(path)
    scan = pytesseract.image_to_string(img)
    if scan or len(scan) > 20:
        dic["scanned_document"] = scan
    else:
        dic["photo"] = "Content of this photo to be classified"

    return dic, img


def excel_extractor(path):
    Dic = {}
    filename = os.path.basename(path)
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        table = pd.read_excel(path, sheet_name=None)
        table = table.replace({np.nan: None})
        Dic = dict(table)
        for k,v in Dic.items():
            Dic[k] = Dic[k].to_json()

    return Dic, table


def table_extractor(path):
    Dic = {}
    filename = os.path.basename(path)
    if filename.endswith("csv") or filename.endswith("tsv"):
        table = pd.read_csv(path, encoding='utf-8')
        if table.columns[0] == 'Unnamed: 0':
            del table['Unnamed: 0']
        table = table.replace({np.nan: None})
        Dic["single_table"] = table.to_dict('index')
    else:
        table = pd.read_table(path)
        if table.columns[0] == 'Unnamed: 0':
            del table['Unnamed: 0']
        table = table.replace({np.nan: None})
        Dic["single_table"] = table

    return Dic, table


def scan_extractor(path):
    paragraph_repo = {}
    s = ''
    # Store all the pages of the PDF in a variable
    pages = convert_from_path(path, 500)

    # Counter to store images of each page of PDF to image
    image_counter = 1

    # Iterate through all the pages stored above
    for page in pages:
        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_1.jpg
        # PDF page 2 -> page_2.jpg
        # PDF page 3 -> page_3.jpg
        # ....
        # PDF page n -> page_n.jpg
        filename = "page_" + str(image_counter) + ".jpg"

        # Save the image of the page in system
        page.save(filename, 'JPEG')

        # Increment the counter to update filename
        image_counter = image_counter + 1

    ''' 
    Part #2 - Recognizing text from the images using OCR 
    '''
    # Variable to get count of total number of pages
    filelimit = image_counter - 1

    # Iterate from 1 to total number of pages
    for i in range(1, filelimit + 1):
        # Set filename to recognize text from
        # Again, these files will be:
        # page_1.jpg
        # page_2.jpg
        # ....
        # page_n.jpg
        filename = "page_" + str(i) + ".jpg"

        # Recognize the text as string in image using pytesserct
        text = str(((pytesseract.image_to_string(Image.open(filename)))))

        # The recognized text is stored in variable text
        # Any string processing may be applied on text
        # Here, basic formatting has been done:
        # In many PDFs, at line ending, if a word can't
        # be written fully, a 'hyphen' is added.
        # The rest of the word is written in the next line
        # Eg: This is a sample text this word here GeeksF-
        # orGeeks is half on first line, remaining on next.
        # To remove this, we replace every '-\n' to ''.
        text = fix_text(text.replace('-\n', ''))
        paragraph_repo[str(i)] = text
        s += text

    return paragraph_repo, s


def get_content(path):
    text = {}
    print(path)
    if path.endswith(".pptx") or path.endswith(".ppt"):
        # try:
        text, raw = ppt_extractor(path)
        file_type = "txt"
        # except Exception as e:
        #     print(e)
        #     pass

    elif path.endswith(".pdf"):

        # try:
        text, raw = pdf_extractor(path)
        if raw == '':
            text, raw = scan_extractor(path)
        file_type = "txt"
        # except Exception as e:
        #     print(e)
        #     try:
        #         text = scan_extractor(path)
        #     except Exception as ee:
        #         print(ee)
        #         pass

    elif path.endswith(".docx"):

        # try:
        text, raw = docx_extractor(path)
        file_type = "txt"
        # except Exception as e:
        #     print(e)
        #     pass

    elif path.endswith(".txt"):

        # try:
        text, raw = txt_extractor(path)
        file_type = "txt"
        # except Exception as e:
        #     print(e)
        #     pass

    elif path.endswith(".png") \
            or path.endswith(".jpeg") \
            or path.endswith(".jpg"):

        text, raw = img_extractor(path)
        file_type = "img"

    elif path.endswith(".tsv") \
            or path.endswith(".csv"):
        # try:
        text, raw = table_extractor(path)
        file_type = "table"
        # except Exception as e:
        #     print(e)

    elif path.endswith(".xls")\
            or path.endswith(".xlsx"):

        text, raw = excel_extractor(path)
        file_type = "sheets"

    else:
        pass
    return text, raw, file_type
