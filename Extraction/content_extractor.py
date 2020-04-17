from __future__ import print_function
import re
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
    vector = {}
    paragraph_nb = 1
    for paragraph in tree.getiterator(PARA):
        texts = None
        text = ""
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            text = ''.join(texts)
            doc[str(paragraph_nb)] = fix_text(text)
            if vectors:
                vector[str(paragraph_nb)] = vectorizer(text, lang=detect(text))
            else:
                pass
            paragraph_nb += 1

    if vectors:
        return creator, doc, vector
    else:
        return creator, doc


def ppt_extractor(path):
    f = open(path, "rb")
    prs = Presentation(f)
    s = ''
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                s += str("new" + shape.text)

    return s


def txt_extractor(path):
    s = ""
    with open(path) as f:
        lines = f.read()

    texts = lines.strip().split("/n/n")
    for text in texts:
        s += str("new" + text)

    return s


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
    s = ""

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        text = ''
        interpreter.process_page(page)

        text = retstr.getvalue()
        retstr.truncate(0)
        text = re.sub(u'(\u0000)', "", text)
        s += str("new" + text)

    fp.close()
    device.close()
    retstr.close()

    return s


def excel_extractor(path):
    OrderedDic = pd.read_excel(path, sheet_name=None)
    Dic = dict(OrderedDic)
    s = ""
    for k, v in Dic.items():
        if v:
            s += str("new" + v)
        else:
            pass

    return s


def scan_extractor(path):
    pages = convert_from_path(path, 500)
    s = ""

    for page in pages:
        text = image_to_string(page)
        s += str("new" + text)

    return s


def get_text(path):
    if path.endswith(".pptx") or path.endswith(".ppt"):
        try:
            text = ppt_extractor(path)
        except Exception as e:
            print(e)
            pass

    elif path.endswith(".pdf"):
        try:
            text = pdf_extractor(path)
        except Exception as e:
            print(e)
            try:
                text = scan_extractor(path)
            except Exception as ee:
                print(ee)
                pass

    elif path.endswith(".docx"):
        try:
            text = docx_extractor(path)
        except Exception as e:
            print(e)
            pass

    elif path.endswith(".txt"):
        try:
            text = txt_extractor(path)
        except Exception as e:
            print(e)
            pass

    elif path.endswith(".xls") or path.endswith(".xlsx"):
        try:
            text = excel_extractor(path)
        except Exception as e:
            print(e)
    return text