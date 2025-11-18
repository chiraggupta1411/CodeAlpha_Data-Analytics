🌐 Web Scraping — CodeAlpha Task 1

This project scrapes the IMDb Top 250 Movies list using Python.
It demonstrates the ability to extract structured data from a website and convert it into a clean dataset.

Features

Fetches the IMDb Top 250 page

Extracts movie Rank, Title, Year, Rating, IMDb ID, and URL

Saves results into imdb_top250.csv, imdb_top250.json, and imdb_top250.xlsx

Includes optional Selenium fallback for dynamic content

Easy to modify for other websites

Technologies

Python

Requests

BeautifulSoup

Pandas

Selenium (optional fallback)

How to Run

Install dependencies:

pip install requests beautifulsoup4 pandas


(Optional for dynamic version)

pip install selenium webdriver-manager


Run the script:

python web_scraping.py


Output files will be saved as:

imdb_top250.csv  
imdb_top250.json  
imdb_top250.xlsx

Outcome

The scraper successfully collects structured IMDb movie data that can be used for:

Data analysis

Visualizations

Recommendation systems

Research or academic projects

It serves as a complete and clean demonstration of web scraping for the CodeAlpha internship.
