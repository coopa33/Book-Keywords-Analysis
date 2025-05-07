from download_webpage import simple_get
from bs4 import BeautifulSoup
import pandas as pd
import re
from cs50 import SQL

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
        titles.append(match_title.group(1))
        authors.append(match_author[-1])

# Create relational databases
open("books.db", "w").close()
db = SQL("sqlite:///books.db")
db.execute("CREATE TABLE authors (id INTEGER, name TEXT, PRIMARY KEY(id))")
db.execute("CREATE TABLE books (book_id INTEGER, title TEXT, PRIMARY KEY(book_id))")

for title in titles:
    print(title)
    title = title.strip().upper()
    id  = db.execute("INSERT INTO books (title) VALUES(?)", title)
for author in authors:
    author = author.strip().upper()
    id = db.execute("INSERT INTO authors (name) VALUES(?)", author)
