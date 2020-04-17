import string
import unidecode
from ftfy import fix_encoding


def correct_ascii(text):
    printable = set(string.printable)
    text = ''.join(filter(lambda x: x in printable, text))

    return text


def fix_text(text):
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\u2013", "-")
    text = text.replace("\u03d5", "ϕ")
    text = text.rstrip("\n")
    text = text.rstrip("\t")
    text = fix_encoding(text)
    text = unidecode.unidecode(text)
    text = correct_ascii(text)

    return text