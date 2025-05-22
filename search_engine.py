import numpy as np
from scipy import sparse


def keyword_search1(X, feature_names, feature, titles, top_n):
    """ Finds the maximum tf-idf value of a word in the corpus, and returns the name of the title with the maximum value of that word """
    word_idx = int(np.where(feature_names == feature)[0][0])

    X_csc = X if sparse.isspmatrix_csc(X) else X.tocsc()

    start, end = X_csc.indptr[word_idx], X_csc.indptr[word_idx + 1]

    data_slice = X_csc.data[start:end]
    rows_slice = X_csc.indices[start:end]

    k = min(top_n, data_slice.size)
    part = np.argpartition(-data_slice, k - 1)[:k]
    order = part[np.argsort(-data_slice[part])]
 
    return [(titles[rows_slice[i]], float(data_slice[i])) for i in order]


