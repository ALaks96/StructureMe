from __future__ import print_function
import os
import re
import zipfile
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
from datetime import datetime as dt
from pdfminer.pdftypes import resolve1
from pdfminer.pdfparser import PDFParser
from xml.etree import ElementTree as etree
from pdfminer.pdfdocument import PDFDocument


def posix_from_s(element):
    year = element[2:6]
    month = element[6:8]
    day = element[8:10]
    hour = element[10:12]
    minute = element[12:14]
    second = element[14:16]
    date = year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second

    return dt.strptime(date, "%Y-%m-%d %H:%M:%S")


def decoder(element):
    try:
        decoded = element.decode("utf-8")
        decoded = re.sub('\x00', "", decoded)
        decoded = re.sub('0xfe', "", decoded)

    except Exception as e:
        print(e)
        decoded = element.decode("latin-1")
        decoded = re.sub('\x00', "", decoded)
        decoded = re.sub('0xfe', "", decoded)
        decoded = re.sub('þÿ', "", decoded)

    return decoded


def msoffice_metadata(path):
    if zipfile.is_zipfile(path):
        zfile = zipfile.ZipFile(path)
        core_xml = etree.fromstring(zfile.read('docProps/core.xml'))
        app_xml = etree.fromstring(zfile.read('docProps/app.xml'))
        metadata = {}
        metadata['Title'] = os.path.basename(path)
        valid_name = ['Author(s)', 'Created Date', 'Modified Date', 'Last Modified By']

        # Key elements
        core_mapping = {
            'title': 'Title',
            'subject': 'Subject',
            'creator': 'Author(s)',
            'keywords': 'Keywords',
            'description': 'Description',
            'lastModifiedBy': 'Last Modified By',
            'modified': 'Modified Date',
            'created': 'Created Date',
            'category': 'Category',
            'contentStatus': 'Status',
            'revision': 'Revision'
        }
        for element in core_xml.getchildren():
            for key, title in core_mapping.items():
                if key in element.tag:
                    if 'date' in title.lower():
                        text = dt.strptime(element.text, "%Y-%m-%dT%H:%M:%SZ")
                    else:
                        text = element.text
                    print("{}: {}".format(title, text))
                    if title in valid_name:
                        metadata[str(title)] = text

        # Statistical information
        app_mapping = {
            'TotalTime': 'Edit Time (minutes)',
            'Pages': 'Page Count',
            'Words': 'Word Count',
            'Characters': 'Character Count',
            'Lines': 'Line Count',
            'Paragraphs': 'Paragraph Count',
            'Company': 'Company',
            'HyperlinkBase': 'Hyperlink Base',
            'Slides': 'Slide count',
            'Notes': 'Note Count',
            'HiddenSlides': 'Hidden Slide Count',
        }
        for element in app_xml.getchildren():
            for key, title in app_mapping.items():
                if key in element.tag:
                    if 'date' in title.lower():
                        text = dt.strptime(element.text, "%Y-%m-%dT%H:%M:%SZ")
                    else:
                        text = element.text
                    print("{}: {}".format(title, text))
                    if title in valid_name:
                        metadata[str(title)] = text

    return metadata


def pdf_metadata(path):
    metadata = {}
    fp = open(path, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    try:
        metadata['Title'] = decoder(doc.info[0]["Title"])
    except AttributeError:
        title = decoder(resolve1(doc.info[0]["Title"]))
        if title:
            metadata['Title'] = title
        else:
            metadata['Title'] = os.path.basename(path)
    except KeyError:
        metadata['Title'] = os.path.basename(path)

    try:
        metadata['Author(s)'] = decoder(doc.info[0]["Author"])
    except AttributeError:
        author = decoder(resolve1(doc.info[0]["Author"]))
        if author:
            metadata["Author(s)"] = author
        else:
            metadata['Author(s)'] = "Unknown"
    except KeyError:
        metadata["Author(s)"] = "Unknown"

    try:
        metadata['Last Modified By'] = decoder(doc.info[0]["Author"])
    except AttributeError:
        author = decoder(resolve1(doc.info[0]["Author"]))
        if author:
            metadata['Last Modified By'] = author
        else:
            metadata['Last Modified By'] = "Unknown"
    except KeyError:
        metadata['Last Modified By'] = "Unknown"

    try:
        metadata['Created Date'] = posix_from_s(decoder(doc.info[0]["CreationDate"]))
    except AttributeError:
        cdate = posix_from_s(decoder(resolve1(doc.info[0]["CreationDate"])))
        if cdate:
            metadata['Created Date'] = cdate
        else:
            metadata['Created Date'] = "Unknown"
    except KeyError:
        metadata['Created Date'] = "Unknown"

    try:
        metadata['Modified Date'] = posix_from_s(decoder(doc.info[0]["ModDate"]))
    except AttributeError:
        mdate = posix_from_s(decoder(resolve1(doc.info[0]["ModDate"])))
        if mdate:
            metadata['Modified Date'] = mdate
        else:
            metadata['Modified Date'] = "Unknown"
    except KeyError:
        metadata['Modified Date'] = "Unknown"

    return metadata


def get_meta(path):
    filename = os.path.basename(path)
    if filename.endswith('.pdf'):
        try:
            temp = pdf_metadata(path)
        except Exception as e:
            print(e)
    else:
        try:
            temp = msoffice_metadata(path)
        except Exception as e:
            print(e)
    return temp