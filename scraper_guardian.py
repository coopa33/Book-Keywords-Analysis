from download_webpage import simple_get
from bs4 import BeautifulSoup
import requests
import unicodedata
import re
from cs50 import SQL
from tqdm import tqdm


def get_goodreads_description(title):
    """
    Extracts the summary of a book title from the webpage goodreads.
    Assumes that given the correct title and author, the first search entry is the 
    correct book. 
    
    Parameters
    ----------
    title : string
        The book title
    
    Returns
    -------
    text
        Goodread.com book description
    """
    try:
        # Navigate to search page of title, and extract the link to book description
        search_url = f"https://www.goodreads.com/search?utf8=%E2%9C%93&q={title.strip().replace(" ", "+")}&search_type=books"
        search_html = simple_get(search_url)
        search_dom = BeautifulSoup(search_html, 'html.parser')
        
    except Exception as E:
        print(f"Error in extracting DOM for search page")
        assert len(search_url) != 0
        assert len(search_html) != 0
        assert len(search_dom) != 0

    try:
        # We assume that the first entry of every search page using the book title is the book we are looking for.
        posfix = search_dom.find_all("a", class_="bookTitle")[0]["href"]

        # Extract DOM of the summary page
        description_html = simple_get("https://www.goodreads.com" + posfix)
        description_dom = BeautifulSoup(description_html, 'html.parser')

    except Exception as E:
        print("Error in either extracting href to new page or extracting DOM for new page")
        print(search_url)
        a = search_dom.find_all("a", class_='bookTitle')
        print(a)
        print(posfix)
        assert len(description_html) != 0
        assert len(description_dom) != 0
    
    try:
        # Scrape the description and return it
        tag = description_dom.select("[class~=BookPageMetadataSection__description]")
        text = tag[0].find_all("span", class_="Formatted")[0].get_text(separator=" ")

    except Exception as E:
        print("Error with finding the summary tag in the book page")
        assert len(tag) != 0
        assert len(text) != 0

    return text


def remove_problematic_words(text):
    """
    Removes all words from a string that could lead to unicode conflicts in building the query
    
    Parameters
    ----------
    text : string
    
    Returns
    -------
    clean_text : string
        Cleaned text where any words with possible unicode conflicts are removed.
    """
    words = text.split()
    clean_words = []

    for word in words:
    
        # Remove smart apostrophes, normalize to NFD
        norm = unicodedata.normalize('NFD', word)
        
        # Check for apostrophes (straight or curly)
        if "'" in word or "’" in word:
            continue  

        # Check for diacritics 
        if any(unicodedata.combining(c) for c in norm):
            continue  

        clean_words.append(word)

    clean_text = ' '.join(clean_words)

    return clean_text


def scrape_gutenberg(title, author):
    """
    Sends a query to https://gutendex.com to extract the full text of a title from the author.
    
    Parameters
    ----------
    title : string
        The title of the book
    author : string
        The author of the book
    
    Returns
    -------
    text : string
        The full text of the book in question. If the book is not found on Gutendex, returns None.
    """

    try:
        # If there are any unicode conflicts, remove the word in question from either of the parameters
        title = remove_problematic_words(title)
        author = remove_problematic_words(author)

        # Query to Gutendex
        query = f"{title} {author}"
        search_result = requests.get(f"https://gutendex.com/books", params={"search": query})
        data = search_result.json()

        try:
            # Inspect the json file. txt files are stored under differing format names, but all share 'text/plain'. Identify correct format name
            formats = data['results'][0]['formats'].keys()
            txt_format = "text/plain"
            for f in formats:
                if 'text/plain' in f.lower():
                    txt_format = f

            try:
                # Request the txt file. 
                txt_url = data['results'][0]['formats'][txt_format]
                text = requests.get(txt_url).text

                # Cut off irrelevant additions by Gutenberg
                start = "START OF THE PROJECT GUTENBERG EBOOK"
                end = "END OF THE PROJECT GUTENBERG EBOOK"
                start_idx = text.find(start)
                start_idx += len(start)
                end_idx = text.find(end)
                text = text[start_idx:end_idx].strip()

                return text
            
            except Exception as e:
                print(f"Error in extracting txt file")
                return None
                
        except Exception as e:
            print(f"text/plain could not be found in {formats}")
            return None
        
    except Exception as e:
        print(f"Couldn't retrieve! Author: {author}, Title: {title}")
        return None
    
      
def add_gutenberg_SQL(titles, authors):
    """
    Scrape and download all full texts of the corpus. Adds them to the sql table books under books.db. If the full text is not available, set the entry to NILL.
    
    Parameters
    ----------
    titles : iterable
        Iterable of strings, containing all titles in the corpus to be scraped
    authors : iterable
        Iterable of strings, containing all author names of the books to be scraped.
    """

    # Instantiate SQL command object
    db = SQL("sqlite:///books.db")

    # Attempt to scrape full text for every title, and add to sql table
    for title, author in tqdm(zip(titles, authors), total = len(titles)):
        text = scrape_gutenberg(title, author)
        db.execute("UPDATE books SET full_text=? WHERE title=?", text, title)


def get_title_and_author():
    """
    Scrape 100 titles and authors from theguardian page
    
    Returns
    -------
    titles : iterable
        The titles of the top 100 novels, according to theguardian
    authors : iterable
        The author names of the top 100 novels, according to the guardian
    """

    # Download HTML from URL 
    GUARDIAN_URL = "https://www.theguardian.com/books/2015/aug/17/the-100-best-novels-written-in-english-the-full-list"
    html = simple_get(GUARDIAN_URL)
    dom = BeautifulSoup(html, 'html.parser')
    
    # Identify the tag where the title and author name are stored.
    # Seperate titles and authors into seperate lists
    all_p = dom.find_all('p')[1:]
    titles = []
    authors = []
    for i in range(len(all_p)):

        # Scrape only the title of the text where title and name are contained, not the text itself
        if i % 2 == 0:
            text = all_p[i].text

            # Identify title and authors via regex patterns, and extract them. Make sure not to include brackets.
            match_title = re.match(r'\d+\.\s*(.*?)(?=\bby\b(?!.*\bby\b))', text)
            match_author = re.search(r'\bby\s+(.*?)(?:\s*\([^)]*\))?\s*$', text)
            title = match_title.group(1).strip()
            author = match_author.group(1).strip()

            titles.append(title)
            authors.append(author)
    
    return titles, authors


def create_relational_databases():
    """
    Create an sql table called books, under books.db. Table contains the title, author, and goodreads summary of the top 100 novels.
    """

    # Create SQL table
    open("books.db", "w").close()
    db = SQL("sqlite:///books.db")
    db.execute("CREATE TABLE books (book_id INTEGER, title TEXT, description TEXT, author TEXT, PRIMARY KEY(book_id));")

    # Get book information, remive newlines and whitespaces
    titles, authors = get_title_and_author()
    for title, author in tqdm(zip(titles, authors), total = len(titles)):
        title = title.replace('\n', '').replace('\r', '').strip().upper()
        author = author.replace('\n', '').replace('\r', '').strip().upper()
        
        # Use title to get summary, and fill all information into table
        description = get_goodreads_description(title)
        id  = db.execute("INSERT INTO books (title, description, author) VALUES(?, ?, ?);", title, description, author)


# Test
if __name__=="__main__":
    title = "PILGRIM'S PROGRESS"
    author = "JOHN BUNYAN"
    print(scrape_gutenberg(title, author))




        


