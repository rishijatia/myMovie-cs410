"""
    Main Class to Scrape Movies and Actors
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import BeautifulSoup
import logging
import re
import time
import json
import datetime
import numpy as np
from math import ceil

__author__ = "rjatia2"

logger = logging.getLogger('Scraper')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

SESSION = requests.session()    # Persisting session for improved performance
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
SESSION.mount('http://', adapter)
SESSION.mount('https://', adapter)

def get_html_content(url):
    """
    Getter method to get the HTML Content of a particular URL
    :param url: URL String
    :return: String of the HTML Content of URL, or None otherwise
    """
    try:
        page = SESSION.get(url, headers={'User-agent': 'rjatia2'})  # Load the webpage
        data = page.text
        return data
    except:
        return None



def get_age(date_of_birth):
    """
    Returns age of an actor, given his or her date of birth
    :param date_of_birth: Date of Birth in YYYY-MM-DD Format
    :return: Age as a number
    """
    date_obj = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')  # Parse Actor's Date Of Birth
    todays_date = datetime.datetime.now()  # Get today's date
    days_lived = (todays_date - date_obj).days
    age = days_lived / 365
    return age

def get_names_and_urls(main_tag, BASE_URL, parent, url_type):
    """
    Get the Names and URLS of either Movies (if scraping Actor)
    or Actors (if scraping Movies)
    :param main_tag: main_tag of cast/movies
    :param BASE_URL: Base Wikipedia URL
    :param parent: Parent Tag Name for Logging
    :param url_type: True If URL refers to Movie Page, False for Actor Page
    :return: a tuple of names, urls of actors/movies
    """
    # Populating Cast and URLs to Scrape
    scraping_failures = 0
    urls = []
    names = []
    for sub_tag in main_tag:
        # For 'a' delimited strings
        if len(sub_tag.attrs) == 2:
            tag = sub_tag
        else:
            tag = sub_tag.find('a')
        if tag is None:
            scraping_failures += 1  # Count of movies that could not be scraped
            continue
        try:
            name = tag['title']
            url = BASE_URL + tag['href']
        except:
            return False
        urls.append((url, url_type))  # Add More Websites to Scrape
        names.append(name)  # Add cast name of this movie

    if scraping_failures != 0:
        logger.warning("--WARNING--: " + str(scraping_failures) + " Data could not be scraped for " + parent)
    else:
        if url_type:
            logger.info("--INFO--:" + "All Cast Successfully Scraped")
        else:
            logger.info("--INFO--:" + "All Movies for " + parent + " Successfully Scraped")

    return names, urls


def get_table_data(rows, BASE_URL, actor):
    """
    Function to get data of movies from the table
    Table Tag to extract data from
    :param rows: Rows of Table Scraped from Beautiful Soup
    :param BASE_URL: BASE_URL to append to urls
    :return: the names and urls to extract from the tags
    """
    names = []
    urls = []
    scraping_failures = 0
    for row in rows[1:]:
        if row is None:
            scraping_failures += 1  # Count of movies that could not be scraped
            continue
        try:
            movie = row.findAll('td')[1].find('a')
            name = movie['title']
            url = BASE_URL + movie['href']
        except:
            scraping_failures += 1
            continue
        urls.append((url, True))  # Add More Websites to Scrape
        names.append(name)  # Add cast name of this movie
    if len(names) == 0 or len(urls) == 0:
        # No Movies Scraped
        logger.warning("--WARNING--: No Movies found for " + actor)
        return False
    if scraping_failures != 0:
        logger.warning("--WARNING--: " + str(scraping_failures) + " movies could not be scraped for " + actor)
    else:
        logger.info("--INFO--: All Movies Successfully Scraped for " + actor)

    return names, urls


def save_json(scraped_data, description_file, meta_file):
    """
    Function to store the scraped data into a JSON
    :param scraped_data: Data to store as JSON
    :param description_file Filename to store reviews in
    :param meta_file Filename to store meta in
    :return: None
    """
    with open(description_file, 'w+') as file:
        for data in scraped_data:
            line = data['description'] + "\n"
            line = line.encode('utf8')
            file.write(line)
    with open(meta_file, 'w+') as file:
        for data in scraped_data:
            line = data['name'] + "\t" + str(data["gross"]) + "\t" + str(data["release_date"]) + "\t" + str(data['link'])  + "\n"
            line = line.encode('utf8')
            file.write(line)

def parse_raw_amount(raw_amount):
    """
    Function to Parse the Box Office Grossed Amount for a particular movie
    Converts Amounts of various types to digits
    EG: $1.2 million to 1200000
    :param raw_amount: Raw Scraped Grossing Amount
    :return: Grossed Amount of movie if available, else False
    """
    # Raw Amount should begin with dollar sign
    dollar_pattern = re.compile('^\$')
    if dollar_pattern.search(raw_amount) is None:  # No Grossed Amount found
        return False
    if ',' in raw_amount and ' ' in raw_amount:
        raw_amount = raw_amount[: raw_amount.find(' ')]
    # Retrieving grossed amount number
    number_format1 = re.compile('^\$[0-9]+.[0-9]+')  # Decimal Numbers
    # Comma Separated Values
    number_format2 = re.compile('(^\$[0-9][0-9,]*[0-9](\[[0-9]+\]$)+)|(^\$[0-9][0-9,]*[0-9]$)')
    if not number_format2.findall(raw_amount):  # Comma Separated Number not found
        if not number_format1.findall(raw_amount):  # Decimal Value not found
            return False
        else:
            number_value2 = number_format1.findall(raw_amount)[0]
    else:
        number_value = number_format2.findall(raw_amount)[0]

    # Finding Strings with Million/Billion
    millionPattern = re.compile('million')
    billionPattern = re.compile('billion')

    millionFlag = millionPattern.search(raw_amount) is not None
    billionFlag = billionPattern.search(raw_amount) is not None

    if millionFlag:
        # Grossing Amount is in the form 1.23 million
        try:
            number_value2 = re.sub(r'\$','',number_value2)
            number_value2 = float(number_value2) * (10 ** 6)
        except ValueError:
            logger.warning('--WARNING--: Gross Amount of Movie could not be Scraped')
            return False
        return number_value2
    if billionFlag:
        # Grossing Amount is in the form 1231.23 billion
        try:
            number_value2 = re.sub(r'\$', '', number_value2)
            number_value2 = ceil(float(number_value2) * (10 ** 9))
        except ValueError:
            logger.warning('--WARNING--: Gross Amount of Movie could not be Scraped')
            return False
        return number_value2

    # Number is Comma Separated Dollar Amount
    try:
        comma_separated_number = ''
        for num in number_value:
            if num != '':
                comma_separated_number = re.sub('\$', '', num)
                break
        if comma_separated_number == '':
            logger.warning('--WARNING--: Gross Amount of Movie could not be Scraped')
            return False

        # Removing Citations
        if comma_separated_number != '' and '[' in comma_separated_number:
            comma_separated_number = comma_separated_number[:comma_separated_number.find('[')]

        """ Checking if there are alien digits in the
            number by checking if there are only three digits in between
            commas
        """
        split_str = comma_separated_number.split(',')[1:]
        if any(len(item) > 3 for item in split_str):
            logger.warning('--WARNING--: Gross Amount of Movie could not be Scraped (invalid commas)')
            return False
        # Remove commas and convert to integer
        comma_separated_number = int(re.sub(r',', '', comma_separated_number))
    except:
        logger.warning('--WARNING--: Gross Amount of Movie could not be Scraped')
        return False
    return comma_separated_number


def get_actors(movie, data):
    """
    Returns list of actors of a particular movie
    :param movie: Movie Name
    :param data: Data dictionary
    :return: List of actors
    """
    for item in data:
        if item['type'] == 'MOVIE':
            if item['name'] == movie:
                # Get list of actor dictionaries
                actors = []
                for actor in item['cast']:
                    for val in data:
                        if val['type'] == 'ACTOR' and val['name'] == actor:
                            # Creating dictionary for edge weight
                            data_dict = {'name': actor, 'age': val['age']}
                            actors.append(data_dict)
                return actors


class Scraper:

    MOVIES_TO_SCRAPE = 1000   # Number of movies to scrape

    def __init__(self, url, url_type):
        """
        Constructor for Scraper Class
        :param url: starting URL for scraping
        """
        assert isinstance(url, str)
        self.start_url = url
        self.url_type = url_type
        self.visited_set = set()  # Logic for Scraping Efficiently
        self.scraping_queue = []  # Logic for Scraping Efficiently
        self.BASE_URL = "https://en.wikipedia.org"
        self.logger = logging.getLogger('Scraper')
        self.logger.setLevel(logging.DEBUG)
        self.scraped_data = []   # List to store scraped dictionaries

    def scrape_actor(self, url):
        """
        Scrape the url corresponding to a webpage for an actor/actress
        :param url: String URL
        :return: dictionary with required information if successful, False otherwise
        """
        self.logger.debug("--DEBUG--: Scraping Content for Actor from URL " + url)
        web_data = get_html_content(url)  # Get HTML Data for that website
        if not web_data:
            return False
        scraped_website = BeautifulSoup.BeautifulSoup(web_data)

        # Get the Div Corresponding to Filmography
        movies_div = scraped_website.find('span', {'id': re.compile(r'Filmography*')})
        if not movies_div:
            self.logger.warning('--WARNING--: No Movies Found for this Actor')
            return False

        movie_header = movies_div.parent
        movies_in_div = movie_header.findNextSiblings('div')
        movies_in_table = movie_header.findNextSibling('table')
        if not movies_in_table and not movies_in_div:
            self.logger.warning('--WARNING--: No Movies Found for this Actor')
            return False
        try:
            if movies_in_table and movies_in_table['class'] == "wikitable sortable":
                # Movies are in the form of a table
                body = movies_in_table.findAll('tr')
                scraped_tuple = get_table_data(body, self.BASE_URL, actor_name)
            elif len(movies_in_div) >= 2: # Check if movies are in the form of a div, which exists
                movies_in_div = movies_in_div[1]
                # Movies are in the form of a div
                list_of_movies = movies_in_div.findAll('li')
                scraped_tuple = get_names_and_urls(list_of_movies, self.BASE_URL, 'actor_name', True)
            else:
                scraped_tuple = False   # Simulate invalid Parsing
            # Get name of movies for this actor and their WIKI Pages
        except:
            self.logger.info("--INFO--:No movies found for this actor")
            return False
        if not scraped_tuple:
            self.logger.warning('--WARNING--: No Movies Found for this Actor')
            return False
        else:
            movie_names, movie_urls = scraped_tuple[0], scraped_tuple[1]

        actor_dict = {'urls': movie_urls}

        # Disregard incomplete parsing
        if len(movie_urls) == 0:
            return False

        return actor_dict

    def scrape_movie(self, url):
        """
        Scrape the movie corresponding to the current url
        :param url: String URL of the Movie's Wikipedia Page
        :return: dictionary of scraped information if successful, false otherwise
        """
        self.logger.debug("--DEBUG--: Scraping Content for Movie from URL " + url)
        web_data = get_html_content(url)  # Get HTML Data for that website
        if not web_data:
            return False
        scraped_website = BeautifulSoup.BeautifulSoup(web_data)

        descriptions = scraped_website.findAll('p')
        descriptionText = ''
        for description in descriptions:
            descriptionText = descriptionText + description.getText() + " "

        movie_name = scraped_website.find('h1', {'id': 'firstHeading'}).text  # Get Movie name

        stats_table = scraped_website.find('table', {'class': 'infobox vevent'})
        if stats_table is None:
            self.logger.warning('--WARNING--: Movie Grossed Amount not Available')
            grossed_amount = -1
        else:
            grossed_amount_tag = stats_table.findAll('tr')[-1]  # Box Office Tag is the Last tag in the table
            raw_grossed_amount = grossed_amount_tag.find('td').text
            grossed_amount = parse_raw_amount(raw_grossed_amount)
            # Release Date of Movie
            release_date = scraped_website.find('span', {'class': 'bday dtstart published updated'})
            if release_date:
                release_date = release_date.text
            else:
                self.logger.warning('--WARNING--: Release Date could not be scraped')
                return False
            if not grossed_amount:
                grossed_amount = -1
        th_tags = scraped_website.findAll('th')
        starring_tag = None
        for tag in th_tags:
            if tag.text == 'Starring':  # Found the tag "Starring", Cast is two tags after
                starring_tag = tag.nextSibling.nextSibling
                break
        if starring_tag is None:
            self.logger.warning('--WARNING--: Movie Cast could not be scraped.')
            return False
        else:
            cast_list_tags = starring_tag.findAll('a')

        # Get name of actors in this movie and their WIKI Pages
        cast_names, cast_urls = get_names_and_urls(cast_list_tags, self.BASE_URL, movie_name, False)

        movie_dict = {'name': movie_name, 'gross': grossed_amount, 'cast': cast_names, 'urls': cast_urls,
                      'release_date': release_date, 'description': descriptionText}

        # Disregarding Incomplete Parsing
        if movie_dict['gross'] == -1 or len(movie_dict['cast']) == 0 or len(descriptionText) == 0:
            return False

        return movie_dict

    def scrape(self):
        """
        Main Scraping function to scrape multiple pages
        :return none:
        """
        self.scraping_queue.append((self.start_url, self.url_type))  # False represents URL of Actor
        movies_scraped = 0  # Number of actors scraped
        sleep_counter = 100 # Counter to determine when to sleep to avoid Request Blocking

        # Depth First Search Scraping
        while (movies_scraped < self.MOVIES_TO_SCRAPE)\
                and len(self.scraping_queue) != 0:

            url, is_movie = self.scraping_queue.pop()
            if url in self.visited_set: # Visited URL
                continue

            if is_movie:    # Scraping a Movie
                # Invalid Parsing
                ret_dict = self.scrape_movie(url)

                if not ret_dict:
                    continue
                else:
                    ret_dict['type'] = 'MOVIE'
                    ret_dict['link'] = url
                    movies_scraped += 1
                    self.scraped_data.append(ret_dict)

            else:   # Scraping an actor
                ret_dict = self.scrape_actor(url)

                # Invalid Parsing
                if not ret_dict:
                    continue


            self.scraping_queue.extend(ret_dict['urls'])

            #  Avoid Connection Refused Error by Wikipedia robots.txt
            #  Sleeping every 100 successful scrapes
            if sleep_counter < movies_scraped:
                self.logger.info('--INFO--: Scraping sleeping for 15 seconds to avoid spamming URLS.')
                sleep_counter += 100
                time.sleep(15)
                self.logger.info("--INFO--: Movies Scraped: " + str(movies_scraped))

            self.visited_set.add(url)   # Add Current URL to visited.
        self.logger.info("--INFO--: Scraping Complete")
        self.logger.info("--INFO--: Total Movies Scraped: "  + str(movies_scraped))

if __name__ == "__main__":
    print "Enter Wikipedia Movie URL to start scraping from, or 0 to use default URL:"
    start_url = raw_input()
    if start_url == '0':
        start_url = "https://en.wikipedia.org/wiki/Morgan_Freeman"
        start_url_type = False  # False represents Actor
    else:
        start_url_type = True
    scraper_obj = Scraper(start_url, start_url_type)
    scraper_obj.scrape()
    save_json(scraper_obj.scraped_data, "dataset/dataset.dat", "dataset/metadata.dat")
