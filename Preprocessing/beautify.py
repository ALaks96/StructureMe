import string
import unidecode
from ftfy import fix_encoding


def correct_ascii(text):
    # Function to correct potential ascii incoherence
    printable = set(string.printable)
    text = ''.join(filter(lambda x: x in printable, text))

    return text


def fix_text(text):
    # General purpose function to strip text from weird characters/symbols that either were in the content to start
    # with or were generated (by error) when extracting content from file + Encoding fixing
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\x0c", "")
    text = text.replace("\u2013", "-")
    text = text.replace("\u03d5", "ϕ")
    text = text.rstrip("\n")
    text = text.rstrip("\t")
    text = fix_encoding(text)
    text = unidecode.unidecode(text)
    text = correct_ascii(text)

    return text
