import pandas as pd
import numpy as np
import spacy
from spacy.pipeline import Lemmatizer
from cs50 import SQL
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from scipy.sparse import csr_matrix
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def lemmatize(text):
    """ Lemmatize a string text into list of lemmatized word tokens"""

    # Create pos tagging for lemmatization, lemmatize text, and remove stopwords, punctuation symbols, and numerics.
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text.lower().strip())
    lemmas = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.like_num]

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


def tf_idf(corpus):
    """ Creates a documents/token matrix with tf-idf, returns the matrix and a list of tokens"""
    vectorizer = TfidfVectorizer(analyzer = lemmatize)
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    return X, feature_names


def top_k_per_row(csr: csr_matrix, k: int = 25):
    """
    Return, for each row, the indices and scores of the k largest
    non-zero values, sorted high-to-low.

    Parameters
    ----------
    csr : scipy.sparse.csr_matrix
    k   : int                 (how many per row)

    Returns
    -------
    top_idx  : list[np.ndarray]   column indices of top-k terms
    top_data : list[np.ndarray]   tf-idf weights matching top_idx
    """
    indptr  = csr.indptr      # shape (n_rows + 1,)
    indices = csr.indices     # all column indices in one 1-D array
    data    = csr.data        # all non-zero values   in one 1-D array

    top_idx, top_data = [], []
    for r in range(csr.shape[0]):
        start, end   = indptr[r], indptr[r + 1]
        row_vals     = data[start:end]
        row_indices  = indices[start:end]

        if row_vals.size == 0:             # empty row
            top_idx.append(np.empty(0, dtype=int))
            top_data.append(np.empty(0))
            continue

        take = min(k, row_vals.size)       # a row may have < k nnz
        # ---- partial sort: O(N log k) instead of full sort O(N log N)
        part  = np.argpartition(-row_vals, take - 1)[:take]
        order = part[np.argsort(-row_vals[part])]     # final descending order

        top_idx.append(row_indices[order])
        top_data.append(row_vals[order])

    return top_idx, top_data


def create_wordcloud(list_of_words, list_of_values, name):
    wordcloud = WordCloud(background_color="white", width=1000, height=500, random_state=42)
    wordcloud.generate_from_frequencies(dict(zip(list_of_words, list_of_values)))
    plt.axis("off")
    plt.title(f"Title: {name}")
    plt.imshow(wordcloud)
    plt.show()






    

        



