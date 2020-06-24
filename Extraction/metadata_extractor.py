import os
import re
import time
import zipfile
from PIL import Image
from PIL.ExifTags import TAGS
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
    # General purpose function to convert wierdly typed date fromats to json readable posix
    year = element[2:6]
    month = element[6:8]
    day = element[8:10]
    hour = element[10:12]
    minute = element[12:14]
    second = element[14:16]
    date = year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second

    return dt.strptime(date, "%Y-%m-%d %H:%M:%S")


def decoder(element):
    # General purpose function to fix encoding problems like replacing accents with non accented character
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
    # Function to extract metadata for any type of MSOffice file, metadata can be found in the xml structure of the
    # zipfile (the msoffice file) alongside its content
    metadata = {}
    if zipfile.is_zipfile(path):
        zfile = zipfile.ZipFile(path)
        core_xml = etree.fromstring(zfile.read('docProps/core.xml'))
        app_xml = etree.fromstring(zfile.read('docProps/app.xml'))
        metadata['Title'] = os.path.basename(path)
        # Retrieve only the below information
        valid_name = ['Author(s)', 'Created Date', 'Modified Date', 'Last Modified By']

        # Key elements (Optional additional elements)
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
        # Loop through every element of the metadata node within the MSOffice file's xml
        for element in core_xml.getchildren():
            for key, title in core_mapping.items():
                # If element in metadata node corresponds to one of the elements defined in core_mapping, retrieve it
                if key in element.tag:
                    # If element corresponds to a date, convert properly
                    if 'date' in title.lower():
                        text = dt.strptime(element.text, "%Y-%m-%dT%H:%M:%SZ")
                    # Otherwise treat it like any other text element
                    else:
                        text = element.text
                    # Final check to keep only the information we defined at root of the function
                    if title in valid_name:
                        metadata[str(title)] = text

        # Statistical information (Additional information on statistical characteristics)
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
        # Same process as above in parallel metadata node containing file statistics
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
    # Function to retrieve PDF metadata when available
    # Initialize dictionary to contain metadata
    metadata = {}
    fp = open(path, 'rb')
    # initialize PDFParser to extract metadata
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    # Long series of exceptions handling in case of wierd text conversion from PDFParser
    try:
        metadata['Title'] = decoder(doc.info[0]["Title"])
    # If not recognized as text, resolve with built in function resolve1()
    except AttributeError:
        title = decoder(resolve1(doc.info[0]["Title"]))
        # Element retrieved is not null, attribute to metadata key
        if title:
            metadata['Title'] = title
        # Otherwise use simple naïve method
        else:
            metadata['Title'] = os.path.basename(path)
    # If not element corresponds to title in metadata use simple naïve method
    except KeyError:
        metadata['Title'] = os.path.basename(path)

    # Same exception handling as above
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

    # Same exception handling as above
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

    # Same exception handling as above
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

    # Same exception handling as above, however use posix correction function defined at root of script
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


def misc_metadata(path):
    # General purpose function to retrieve elementary metadata from files other than MSOffice & PDF (mainly
    # creation & modification date)
    metadata = {'Title': os.path.basename(path),
                'Author(s)': "Unknown",
                'Last Modified By': "Unknown",
                'Created Date': time.ctime(os.path.getmtime(path)),
                'Modified Date': time.ctime(os.path.getctime(path))}

    return metadata


def get_exif(path):
    exifs = {}
    image = Image.open(path)
    exifdata = image.getexif()
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
    exifs['tags'] = dict(data)

    return exifs


def get_meta(path):
    # Function calling all others depending on file type
    MSoffice = [".pptx", ".ppt", ".docx", ".xls", ".xlsx"]
    filename = os.path.basename(path)
    if filename.endswith('.pdf'):
        temp = pdf_metadata(path)
    elif filename.endswith(tuple(MSoffice)):
        temp = msoffice_metadata(path)
    else:
        temp = misc_metadata(path)
    # temp is a dictionary containing all metadata this program was able to retrieve
    return temp
