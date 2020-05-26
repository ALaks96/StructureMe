import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from Preprocessing.beautify import fix_text


def requirements():
    # Load series of text lists for nlp processing (Lemming, stopwords, ...)
    try:
        stopword_list = stopwords.words('english')

    except Exception as e:
        print(e)
        print("downloading for you!")
        nltk.download('stopwords')
        stopword_list = stopwords.words('english')

    try:
        lemmatizer = WordNetLemmatizer()

    except Exception as e:
        print(e)
        print("downloading for you!")
        nltk.download('wordnet')
        lemmatizer = WordNetLemmatizer()

    special_characters = ["@", "/", "#", ".", ",", "!", "?", "(", ")", "-", "_", "’", "'", "\"", ":", "=", "+", "&",
                          "`", "*", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "'", '.', '‘', ';']

    # Initialize transformation dictionary
    transformation_sc_dict = {initial: " " for initial in special_characters}

    return stopword_list, lemmatizer, transformation_sc_dict


def concat_str_list(l):
    # Function to concatenate all elements of a list seperated with a white-space
    s = ' '.join(l)
    return s


def clean_text(text):
    # Function

    # convert text to lowercase
    text = text.strip().lower()

    # replace punctuation characters with spaces
    filters = '"\'%&()*,-./:;<=>?[\\]^_`{|}~\t\n'
    translate_dict = dict((c, " ") for c in filters)
    translate_map = str.maketrans(translate_dict)
    text = text.translate(translate_map)

    return text


def preprocessing(text):
    stopword_list, lemmatizer, transformation_sc_dict = requirements()

    # Tokenization
    try:
        tokens = word_tokenize(text)
    except Exception as e:
        print(e)
        print("downloading for you!")
        nltk.download('punkt')
        tokens = word_tokenize(text)

    # Deleting words with  only one caracter
    tokens = [token for token in tokens if len(token) > 2]

    # stopwords + lowercase
    tokens = [token.lower() for token in tokens if token.lower() not in stopword_list]

    # Deleting specific characters
    tokens = [token.translate(str.maketrans(transformation_sc_dict)) for token in tokens]

    # Lemmatizing tokens
    try:
        tokens = [lemmatizer.lemmatize(lemmatizer.lemmatize(lemmatizer.lemmatize(token, pos='a'), pos='v'), pos='n') for
                  token in tokens]
    except Exception as e:
        print(e)
        print("downloading for you!")
        nltk.download('wordnet')
        tokens = [lemmatizer.lemmatize(lemmatizer.lemmatize(lemmatizer.lemmatize(token, pos='a'), pos='v'), pos='n') for
                  token in tokens]

    # Final cleaning of additionnal characters
    tokens = [fix_text(clean_text(token)) for token in tokens]

    return concat_str_list(tokens)
