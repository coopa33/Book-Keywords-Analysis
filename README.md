# Book-Keywords-Analysis

Structure:

- The notebook **results.ipynb** contains all analyses and visualizations.
- The scripts **scraper_guardian.py**, **tfidf.py**, **search_enginge.py** and **download_webpage.py** contain function implementations that I use throughout the notebook.
- The **"data/"** directory contains all intermediate data from my analysis.
- The **process_book.ipynb** contains my project progress log.
- The text file **requirements.txt** contains necessary libraries for running all notebooks and scripts
- The md file **description.md** describing the project, research questions, and data sources.

To read my project, please follow the subsequent steps:

1) Make sure to download all of these, and do not change the locations of any of the scripts or datafiles. 
2) Before running the notebook, please install all required libraries in your virtual environment. To do so, run 'pip install -r requirements.txt' from your virtual environment.
3) To view the project, run the jupyer notebook **results.ipynb**.
4) ***WARNING*** Some of the operations in the notebook take a long time! Note that the complete database of all summaries and all full texts are already contained in the sql database **books.db**. So you do not need to run the scraping operations necessarily. However, if you want to run these, it shouldn't take too long. I would definitely **not recommend** running the tf-idf matrix calculations, as they can take **VERY LONG (around 100 minutes for full texts with name exclusion)**. To avoid that, please take note of comments below such operations, as they show you how you can load the same tf-idf matrices from local files that I've previously saved. 
