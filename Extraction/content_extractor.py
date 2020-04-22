import re
import os
import zipfile
import pandas as pd
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
    # vector = {}
    paragraph_nb = 1
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            text = ''.join(texts)
            doc[str(paragraph_nb)] = fix_text(text)
#            if vectors:
#                vector[str(paragraph_nb)] = vectorizer(text, lang=detect(text))
#            else:
#                pass
            paragraph_nb += 1

#    if vectors:
#        return creator, doc, vector
    else:
        return doc


def ppt_extractor(path):
    paragraph_repo = {}
    # vector = {}
    f = open(path, "rb")
    prs = Presentation(f)
    slide_nb = 0
    for slide in prs.slides:

        slide_nb += 1
        temp_text = ''

        for shape in slide.shapes:

            if hasattr(shape, "text") and shape.text.strip():
                temp_text += shape.text

        paragraph_repo[str(slide_nb)] = fix_text(temp_text)
        # if vectors:
        #     vector[str(slide_nb)] = vectorizer(temp_text, lang=detect(text))
        # else:
        #     pass

    # if vectors:
    #     return creator, paragraph_repo, vector
    # else:
    return paragraph_repo


def txt_extractor(path):
    doc = {}
    # vector = {}
    paragraph_nb = 1

    with open(path) as f:
        lines = f.read()

    texts = lines.strip().split("/n/n")
    for text in texts:
        doc[str(paragraph_nb)] = fix_text(text)
        # if vectors:
        #     vector[str(paragraph_nb)] = vectorizer(text, lang=detect(text))
        # else:
        paragraph_nb += 1

    # if vectors:
    #     return doc, vector
    # else:
    return doc


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

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        text = ''
        interpreter.process_page(page)

        text = retstr.getvalue()
        retstr.truncate(0)
        text = re.sub(u'(\u0000)', "", text)
        paragraph_repo[str(current_page_number)] = fix_text(text)
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
    return paragraph_repo


def table_extractor(path):
    Dic = {}
    filename = os.path.basename(path)
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        OrderedDic = pd.read_excel(path, sheet_name=None)
        Dic = dict(OrderedDic)
        for k,v in Dic.items():
            Dic[k] = Dic[k].to_json()
    elif filename.endswith("csv"):
        table = pd.read_csv(path, encoding='utf-8')
        Dic["single_table"] = table.to_dict('index')
    else:
        table = pd.read_table(path)
        Dic["single_table"] = table

    return Dic


def scan_extractor(path, vectors=False):
    pages = convert_from_path(path, 500)
    paragraph_repo = {}
    # vector = {}
    current_page_number = 1

    for page in pages:
        text = image_to_string(page)
        paragraph_repo[str(current_page_number)] = text

        # if vectors:
        #     vector[str(current_page_number)] = vectorizer(text, lang=detect(text))

    # if vectors:
    #     return paragraph_repo, vector
    #
    # else:
    return paragraph_repo


def get_content(path):
    text = {}
    print(path)
    if path.endswith(".pptx") or path.endswith(".ppt"):
        # try:
        text = ppt_extractor(path)
        # except Exception as e:
        #     print(e)
        #     pass

    elif path.endswith(".pdf"):

        # try:
        text = pdf_extractor(path)
        # except Exception as e:
        #     print(e)
        #     try:
        #         text = scan_extractor(path)
        #     except Exception as ee:
        #         print(ee)
        #         pass

    elif path.endswith(".docx"):

        # try:
        text = docx_extractor(path)
        # except Exception as e:
        #     print(e)
        #     pass

    elif path.endswith(".txt"):

        # try:
        text = txt_extractor(path)
        # except Exception as e:
        #     print(e)
        #     pass

    elif path.endswith(".xls")\
            or path.endswith(".xlsx")\
            or path.endswith(".csv"):

        # try:
        text = table_extractor(path)
        # except Exception as e:
        #     print(e)
    else:
        pass
    return text
