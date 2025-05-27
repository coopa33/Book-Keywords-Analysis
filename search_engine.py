import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


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


def profile_books(collection_indices, book_titles, tfidf_mat):
    
    profile = tfidf_mat[collection_indices].mean(axis=0)
    print(profile.shape)
    print(type(profile))
    profile = profile.reshape(1, -1)

    return profile

def similar_books(collection, book_titles, tfidf_mat, n):

    indices = []
    for book in collection:
        indices.append(list(book_titles).index(book))

    # Create reader profile
    profile = profile_books(indices, book_titles, tfidf_mat)

    # Calculate cosine similarity of whole corpus to profile
    cos_sim = cosine_similarity(profile, tfidf_mat).flatten()

    # Sort by descending similarity, remove profile books, and only chose the top n
    sim_indices = cos_sim.argsort()[::-1]
    sim_indices = [idx for idx in sim_indices if idx not in indices][:n]
    

    recommends = book_titles.iloc[sim_indices]

    return recommends




    



