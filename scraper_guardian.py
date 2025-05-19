from download_webpage import simple_get
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from cs50 import SQL


def get_goodreads_description(title):
    """
    Extracts the description of a book title from the webpage goodreads.
    Assumes that given the correct title name, the first search entry is the 
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
        search_url = f"https://www.goodreads.com/search?utf8=%E2%9C%93&q={title.replace(" ", "+")}&search_type=books"
        search_html = simple_get(search_url)
        search_dom = BeautifulSoup(search_html, 'html.parser')

        # We assume that the first entry of every search page using the book title is the book we are looking for.
        posfix = search_dom.find_all("a", class_="bookTitle")[0]["href"]
        
        # Navigate to description page and extract description
        description_html = simple_get("https://www.goodreads.com" + posfix)
        description_dom = BeautifulSoup(description_html, 'html.parser')
        tag = description_dom.select("[class~=BookPageMetadataSection__description]")
        text = tag[0].find_all("span", class_="Formatted")[0].get_text(separator=" ")
    except Exception as E:
        print(E, type(E))

    return text



def get_title_and_author():

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
        if i % 2 ==0:
            text = all_p[i].text
            match_title = re.match(r'\d+\.\s*(.*?)(?=\bby\b(?!.*\bby\b))', text)
            match_author = re.findall(r'\bby\b\s*(.*?)(?:\s*\(\d{4}\))?\s*$', text)
    
            # Check if extracted titles are unique
            if match_title.group(1) not in titles:
                titles.append(match_title.group(1))
            if match_author[-1] not in authors:
                authors.append(match_author[-1])
    
    return titles, authors


def create_relational_databases():

    # Create relational databases
    open("books.db", "w").close()
    db = SQL("sqlite:///books.db")
    db.execute("CREATE TABLE authors (id INTEGER, name TEXT, PRIMARY KEY(id));")
    db.execute("CREATE TABLE books (book_id INTEGER, title TEXT, description TEXT, PRIMARY KEY(book_id));")
    titles, authors = get_title_and_author()
    for title in titles:
        title = title.strip().upper()
        id  = db.execute("INSERT INTO books (title) VALUES(?);", title)
        description = get_goodreads_description(title)
        db.execute("UPDATE books SET description = ? WHERE title = ?;", description, title)
    for author in authors:
        author = author.strip().upper()
        id = db.execute("INSERT INTO authors (name) VALUES(?);", author)



if __name__=="__main__":
    create_relational_databases()
    
        


