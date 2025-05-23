import spacy

import re
from cs50 import SQL
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import words
import nltk
import logging

# Download nltk set of words, and set as global set
nltk.download('words')

def lemmatize(text):
    """ Lemmatize a string text into list of lemmatized word tokens"""

    custom_stopwords = {
    "say", "tell", "shall", "mr", "mrs", "like", "know", "think", "see", "look",
    "come", "go", "leave", "time", "day", "man", "thing", "good", "old", "little",
    "great", "o", "eye", "hand"
    }


    # Create pos tagging for lemmatization, lemmatize text, and remove stopwords, punctuation symbols, and numerics.
    lemmas = []
    nlp = spacy.load('en_core_web_sm')
    nlp.max_length = 2_000_000  
    doc = nlp(text.lower().strip())
    for token in doc:
        lemma = token.lemma_
        if len(lemma) > 2 and not token.is_stop and not token.is_punct and not token.like_num and re.match(r'^[a-zA-Z]+$', lemma) and not lemma in custom_stopwords:
            lemmas.append(lemma)


    # lemmas = [token.lemma_.lower().strip() for token in doc if 
    #           token.lemma_ in ENG_WORDS and 
    #           not token.is_stop and 
    #           not token.is_punct and 
    #           not token.like_num and 
    #           re.match(r'^[a-zA-Z]+$', token.lemma_) and
    #           token.lemma_]

    return lemmas


def stopword_list(corpus): # Not necessary since lemmatize() already filters out stopwords
    """ Returns a list of stopwords, punctuation words, and numerics in the corpus"""
    nlp = spacy.load('en_core_web_sm')

    corpus = " ".join(corpus)
    doc = nlp(corpus)
    stop_words = [token.text for token in doc if token.is_stop]
    punctuations = [token.text for token in doc if token.is_punct]
    numerics = [token.text for token in doc if token.like_num]

    return stop_words + punctuations + numerics


def load_table(sql_datapath, table_name):
    """Loads sql database into list of dictionaries"""

    db = SQL(f'sqlite:///{sql_datapath}')
    sql_list = db.execute(f'SELECT * FROM {table_name};')

    return sql_list
    
    
def extract_column(sql_list, column_name):
    """ Extracts a specific column from a table in an sql database """

    column = [dict[column_name] for dict in sql_list]

    return column


def tf_idf(corpus, max_df):
    """ Creates a documents/token matrix with tf-idf, returns the matrix and a list of tokens"""

    # Use GPU for spacy, comment out if no dedicated GPU is available.
    spacy.prefer_gpu()
    vectorizer = TfidfVectorizer(analyzer = lemmatize, max_df=max_df)
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    
    return X, feature_names


def max_row(df, n, index = False):
    df_max = df.copy(deep=True)
    if index:
        df_max = df.apply(lambda x: 
                 x.nlargest(n).index.tolist(), axis = 1)
    else:
        df_max = df.apply(lambda x: 
                 x.nlargest(n).values, axis = 1)
    return df_max


def create_wordcloud(list_of_words, list_of_values, name):
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    wordcloud = WordCloud(background_color="white", width=1000, height=500, random_state=42)
    wordcloud.generate_from_frequencies(dict(zip(list_of_words, list_of_values)))
    plt.axis("off")
    plt.title(f"Title: {name}")
    plt.imshow(wordcloud)
    plt.show()

if __name__ == "__main__":
    print("Heathcliff" in ENG_WORDS)





    

        



