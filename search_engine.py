import numpy as np

def keyword_search(X, feature_names, feature, titles):
    """ Finds the maximum tf-idf value of a word in the corpus, and returns the name of the title with the maximum value of that word """
    word_idx = np.where(feature_names == feature)[0]
    col_vec = X.getcol(word_idx)
    k = col_vec.data.argmax()
    row_idx = col_vec.indices[k]
    return titles[row_idx]


