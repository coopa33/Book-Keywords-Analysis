import spacy
from cs50 import SQL
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import logging
from IPython.display import display, HTML

nlp = spacy.load('en_core_web_sm')
nlp.max_length = 2_100_000 


def lemmatize(text):
    """ Lemmatize a string text into list of lemmatized word tokens"""

    lemmas = [] 

    # Fit nlp model
    doc = nlp(text.strip())

    # Apply filters to remove unwanted tokens
    for token in doc:
        lemma = token.lemma_
        if len(lemma) > 2 and not token.is_stop and not token.is_punct and not token.like_num and lemma.isalpha():
            lemmas.append(lemma)

    return lemmas


def lemmatize_no_names(text):
    """ Lemmatize a string text into list of lemmatized word tokens, filtering out names"""

    lemmas = []

    # Fit nlp model
    doc = nlp(text.strip())

    # Use doc.ents to create a set of named entities, and filter out tokens that are names
    names = {ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON"}

    # Apply filters to remove unwanted tokens
    for token in doc:
        lemma = token.lemma_.lower() # Now lower before calculating tf_idf, since we exclude names
        if len(lemma) > 2 and not token.is_stop and not token.is_punct and not token.like_num and lemma.isalpha() and lemma not in names:
            lemmas.append(lemma)

    return lemmas


def tf_idf(corpus, max_df, analyzer = lemmatize):
    """
    Creates a documents/token matrix of tf-idf scores. 
    
    Parameters
    ----------
    corpus : iterable
        An iterable of all documents, in string format
    max_df : float
        Maximum document frequency allowed for each token    

    Returns
    -------
    X : sparse.matrix
        The tf-idf matrix (titles, tokens) in sparse form
    feature_names : iterable
        An iterable of all the unique tokens in the matrix
    """
    
    # Instantiate the Vectorizer, specifying the tokenization function and max_df
    vectorizer = TfidfVectorizer(analyzer = analyzer, max_df=max_df)

    # Create Bag of Words, and compute tf-idf for each token in each document, and extract unique tokens
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    
    return X, feature_names


def load_table(sql_datapath, table_name):
    """
    Loads sql database into list of dictionaries
    
    Parameters
    ----------
    sql_datapath : string
        Path to the sql file
    table_name : string
        The table to extract in the sql file

    Returns 
    -------
    sql_list : list
        A list of all rows of the table, as dictionaries, where keys denote the particular column of that row, and their values are the entries.
    """

    # SQL interface object
    db = SQL(f'sqlite:///{sql_datapath}')
    sql_list = db.execute(f'SELECT * FROM {table_name};')

    return sql_list
    
    
def extract_column(sql_list, column_name):
    """ 
    Extracts a specific column from a table in an sql database 

    Parameters
    ----------
    sql_list : iterable
        An iterable of dictionaries, each being one row in an sql table. The output of load_table().
    column_name : string
        The name of the column you want to extract from the sql table.

    Returns
    -------
    column : list
        A list of all entries of that column in the sql table
    """

    column = [dict[column_name] for dict in sql_list]

    return column


def scroll_df(df, height = '500px'):
    """
    Allows displaying dataframes in a scrollable html output. Convenient, as we have dataframes with many entries.
    """
    
    # Specify tags and style, allowing overflow in y-axis
    display(HTML(f"""
            <div style="height: {height}; overflow-y: auto; border: 1px solid #ccc">
                {df.to_html()}
            </div>
        """))




def max_row(df, n, index = False):
    """
    Takes a TF-IDF dataframe(!) and outputs a Series of lists. Each list contains n tokens with the highest TF-IDF scores for the book that the list belongs to. 

    Parameters:
    -----------
    df : pd.DataFrame
        TF-IDF dataframe (books, tokens)
    n : int
        Number of keywords for each book
    index : bool
        If True, function returns tokens. If False, function returns TF-IDF values. 

    Returns
    -------
    df_max : pd.Series
        Series of either lists of either n-keywords or n-TF-IDF values.
    """

    # Making changes to dataframe, therefore deep copy
    df_max = df.copy(deep=True)

    # Depending on index, either compute and return n-words with highest tf-idf, or n-highest tf-idf values for the whole corpus
    if index:
        df_max = df.apply(lambda x: 
                 x.nlargest(n).index.tolist(), axis = 1)
    else:
        df_max = df.apply(lambda x: 
                 x.nlargest(n).values, axis = 1)
    return df_max


def create_wordcloud(top_15_tokens, top_15_tfidf, titles, selection):

    """
    Create wordclouds of 15 keywords for a given title

    
    Parameters
    ----------
    list_of_words : iterable
        An iterable of 15 words of the book with the highest tf-idf values.
    list_of_values : iterable
        An iterable of the 15 highest tf-idf values found in the book
    name : string
        The name of the book 
    """
    # Remove any debug messages that might occur and clog the notebook
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # Instantiate wordcloud object
    wordcloud = WordCloud(background_color="white", width=1000, height=500, random_state=42)

    # Plot wordclouds for every title selected
    for title in selection:
        idx = list(titles).index(title)
        tokens = top_15_tokens[idx]
        tfidf = top_15_tfidf[idx]

        # Generate
        wc = wordcloud.generate_from_frequencies(dict(zip(tokens, tfidf)))

        # Plot
        plt.axis("off")
        plt.title(f"Title: {title}")
        plt.imshow(wc)
        plt.show()
        

def compare_wordclouds(summary_tokens, summary_tfidf, full_tokens, full_tfidf, summary_titles, full_titles, selection):
    """
    Make comparative wordcloud images, comparing summary to full text keywords
    
    Parameters
    ----------
    summary_tokens : iterable
        List of 15 keywords for each summary
    summary_tfidf : iterable
        List of the 15 highest tf-idf values for each summary
    full_tokens : iterable
        List of 15 keywords for each full text
    full_tfidf : iterable
        List of the 15 highest tf-idf values for each full text
    summary_titles : iterabls
        List of all summary titles
    full_titles : iterable
        List of all full text titles
    selection : iterable
        List of selected books to plot wordclouds for
    """

    # Remove any debug messages that might occur and clog the notebook
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # Instantiate two wordcloud objects
    wc1 = WordCloud(background_color="white", width=1000, height=500, random_state=42)
    wc2 = WordCloud(background_color="white", width=1000, height=500, random_state=42)

    # For each selected title, generate wordclouds
    for title in selection:
        try:
            # Extract title indices and select respective tokens and tf-idf scores
            sum_idx = list(summary_titles).index(title)
            full_idx = list(full_titles).index(title)
            select_sum_tokens = summary_tokens[sum_idx]
            select_sum_tfidf = summary_tfidf[sum_idx]
            select_full_tokens = full_tokens[full_idx]
            select_full_tfidf = full_tfidf[full_idx]

            # Generate
            wc1 = wc1.generate_from_frequencies(dict(zip(select_sum_tokens, select_sum_tfidf)))
            wc2 = wc2.generate_from_frequencies(dict(zip(select_full_tokens, select_full_tfidf)))

            # Plot
            fig, axs = plt.subplots(1, 2, figsize=(10, 5))
            axs[0].imshow(wc1, interpolation='bilinear')
            axs[0].axis('off')
            axs[0].set_title(f"{title} : Summary")
            axs[1].imshow(wc2, interpolation='bilinear')
            axs[1].axis('off')
            axs[1].set_title(f"{title} : Full text")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"The title {title} is not present in both databases.")

        










    

        



