# Book-Keywords-Analysis

This project looks at the "100 best novels" of all time, as defined by Robert McCrum in theGuardian in 2015 ([link to article](https://www.theguardian.com/books/2015/aug/17/the-100-best-novels-written-in-english-the-full-list)) and determine the most characteristic words of each novel. Characteristic words are defined as the words "most informative" of the content of the book's summary/text. 

Informativeness of the keywords are determined using the common ratio "Term-Frequency / Inverse Document Frequency" (TF-IDF), in essence a metric that compares the frequency of a word in a novel compared to the sparsity of that word in other novels. A high ratio is indicative of the word being common in the novel text, but uncommon in the overall corpus of novels, in other words, the word is comparatively unique to the novel, and thus a suitable keyword. For more on TF-IDF see [here](https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/)

In doing this, I am interested in the following questions:
- What are the most characteristic words for each of the top 100 novels?
- Are summaries a good text base to obtain characteristic words that are informative?
- How does the informativeness of characteristic words differ when using summaries compared to full texts?
- Can I use TF-IDF scores to make book recommendations from my database?

The notebook **results.ipynb** contains all analyses and visualizations. The scripts **scraper_guardian.py** and **tfidf.py** contain function implementations that I use throughout the notebook. The "data/" directory contains all intermediate data from my analysis. The **process_book.ipynb** contains my project progress log. 
