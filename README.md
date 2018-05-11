# myMovie

## Rishi Jatia

### Motivation

The motivation for myMovie is to be able to search for movies based on preferences of users such as based on reviews, ratings, theme, genre, cast or keywords. myMovie is a Vertical Search Engine specifically for movies that are crawled from Wikipedia. 

Sample queries that can be used are:

* superhero movies with Christian Bale
* indian movies
* romantic movies that are good

### Tech Stack

myMovie uses MeTapy to index and search for movie data. It uses BeautifulSoup in Python to scrape data from Wikipedia and uses Flask to serve the application on the web.

It adapts form the [MeTa Search Demo](https://github.com/meta-toolkit/metapy-demos) and creates configuration files to parse scraped movie data, adapts the Search Interface to provide a more realistic list-like appearance and adds simple styling to the landing HTML. 

### Functions and Structure

The parts of the project and their purpose are as follows:

* `search_server.py`
    * Contains the code for serving the website over Flask

* `searcher.py`
    * Contains the code to use the inverted index and MeTa package to search for relevant documents based on the query

* `dataset/`
    * Contains scraped movie data

* `Scraper.py`
    * Contains code for scraping Wikipedia for movie data

* `static/`
    * Contains the HTML and JavaScript for rendering the Webpage

* `static/search/javascript/index.js`
    * Contains the JavaScript to process the results, query the backend and display the results.

* `config.toml`
    * Contains the MeTa configuration file for the dataset.

### Initial Setup

These setup instructions are for MacOS Users and UNIX users, but can be adapted for other platforms too.

1. Install pip by downloading [get-pip.py](https://raw.github.com/pypa/pip/master/contrib/get-pip.py), changing into the directory of the `get-pip.py` script and running:

```bash
python get-pip.py
```

2. Run the following command:

```bash
pip install -r requirements.txt
```
The initial setup in order to build this project is ready.

### Running & Scraping

1. To build and run the project, run:

```bash
python search_server.py config.toml
```

This should open up the search interface on http://127.0.0.1:5000/

2. To Scrape and update data, run and use the command line interface:

```bash
python Scraper.py
```

Once scraping is complete, the data automatically gets updated in the `dataset/` folder and the search engine runs with new information in the next run.


### Function Documentation

A Doxygen has been generated for this project to view the documentation of the functions and scripts. 

To view documentation, open `html/index.html` in a browser.

### Contributing

To contribute to this project, kindly clone the repository and create pull requests/issues. All help is welcome!
