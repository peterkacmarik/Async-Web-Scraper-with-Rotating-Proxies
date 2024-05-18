from multiprocessing import Pool
import numpy as np
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import os
import logging
from logs import logger
from config import load_settings
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Load logger settings from .env file
LOG_DIR_SCRAPING = os.getenv('LOG_DIR_SCRAPING')

# Create logger object
logger = logger.get_logger(log_file=LOG_DIR_SCRAPING, log_level=logging.INFO)


class DataScraper:
    def __init__(self, pages_responses: List[str]) -> None:
        """
        Initializes a new instance of the class.

        Args:
            pages_responses (List[str]): A list of HTML responses from web pages.

        Returns:
            None

        Initializes the instance variables `pages_responses`, `base_url`, and `results_all_urls` with the given values.
        """
        self.pages_responses = pages_responses
        self.base_url = load_settings()['scraping_settings']['base_url']
        self.results_all_urls = []
        
    
    def get_url(self):
        """
        This function scrapes URLs from the pages in `self.pages_responses` and appends them to `self.results_all_urls`.

        It iterates over each response in `self.pages_responses` and checks if it is not empty. If it is not empty, it creates a BeautifulSoup object from the response and finds all the elements with the class 'bookitem span2'. It then iterates over each of these elements and finds the 'href' attribute of the 'a' tag with the class 'title-name'. The found URL is appended to `self.results_all_urls`.

        The function returns `self.results_all_urls`, which contains all the scraped URLs.

        Parameters:
        - None

        Return Type:
        - List[str]: A list of scraped URLs.
        """
        for response in self.pages_responses:
            if response:
                soup: BeautifulSoup = BeautifulSoup(response, 'html.parser')
                start_point: List = soup.find_all('div', class_='bookitem span2')
                for url in start_point:
                    self.results_all_urls.append(self.base_url + url.find('a', class_='title-name').get('href'))
        logger.info(f'Number of URLs: {len(self.results_all_urls)}')
        return self.results_all_urls
    
    
    def get_url_details(self):
        """
        Extracts detailed information from a list of HTML responses.

        Returns:
            dict: A dictionary containing the following keys:
                - 'username' (list): List of usernames.
                - 'user_url' (list): List of user URLs.
                - 'lokalita' (list): List of locations.
                - 'cena' (list): List of prices.
                - 'nazev' (list): List of titles.
                - 'autor' (list): List of authors.
                - 'rok1' (list): List of first year of publication.
                - 'rok2' (list): List of second year of publication.
                - 'nakladatel' (list): List of publishers.
                - 'vydani0' (list): List of first edition.
                - 'vydani1' (list): List of second edition.
                - 'vydani2' (list): List of third edition.
                - 'jazyk0' (list): List of first language.
                - 'jazyk1' (list): List of second language.
                - 'jazyk2' (list): List of third language.
                - 'jazyk3' (list): List of fourth language.
                - 'isbn' (list): List of ISBNs.
                - 'isbn0' (list): List of first ISBN.
                - 'isbn1' (list): List of second ISBN.
                - 'isbn2' (list): List of third ISBN.
                - 'isbn3' (list): List of fourth ISBN.
                - 'isbn4' (list): List of fifth ISBN.
                - 'isbn5' (list): List of sixth ISBN.
                - 'book_url' (list): List of book URLs.
        """
        detail_data = {
            'username': [],
            'user_url': [],
            'lokalita': [],
            'cena': [],
            'nazev': [],
            'autor': [],
            'rok1': [],
            'rok2': [],
            'nakladatel': [],
            'vydani0': [],
            'vydani1': [],
            'vydani2': [],
            'jazyk0': [],
            'jazyk1': [],
            'jazyk2': [],
            'jazyk3': [],
            'isbn': [],
            'isbn0': [],
            'isbn1': [],
            'isbn2': [],
            'isbn3': [],
            'isbn4': [],
            'isbn5': [],
            'book_url': []
        }
        for response in self.pages_responses:
            soup: BeautifulSoup = BeautifulSoup(response, 'html.parser')
            
            start_point: List = soup.find_all('div', class_='span6 asmaro clearfix')
            for point in start_point:
                detail_data['username'].append(point.find('a')['data-username'])
                detail_data['user_url'].append(self.base_url + point.find('a')['href'])
                detail_data['lokalita'].append(point.find('span', class_='ask-detail-trigger').text.strip())
                detail_data['cena'].append(point.find('div', class_='ask-col-price').text.strip().replace(' Kč', ''))
                detail_data['book_url'].append(self.base_url + '/kniha/' + soup.find('div', class_='ask-col-actions').find('a')['data-issue-id'])
                try:
                    detail_data['nazev'].append(soup.find('div', class_='page-header span12').find('h1').text.strip().replace('\n\t\t\t\n\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t', ' '))
                except:
                    detail_data['nazev'].append(np.nan)
                try:
                    detail_data['autor'].append(soup.find('div', class_='span3').text.strip().replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', ' ').replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', ' '))
                except:
                    detail_data['autor'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[0].text.strip().split('\n\n')[0] == 'nakladatel':
                        detail_data['nakladatel'].append(soup.find('table', class_='table table-striped').find_all('tr')[0].text.strip().split('\n\n')[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[0].text.strip().split('\n\n')[0] != 'nakladatel':
                        detail_data['nakladatel'].append(np.nan)
                except:
                    detail_data['nakladatel'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[1].text.strip().split('\n')[0] == 'rok vydání':
                        detail_data['rok1'].append(soup.find('table', class_='table table-striped').find_all('tr')[1].text.strip().split('\n')[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[1].text.strip().split('\n')[0] != 'rok vydání':
                        detail_data['rok1'].append(np.nan)
                except:
                    detail_data['rok1'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n')[0] == 'rok vydání':
                        detail_data['rok2'].append(soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n')[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n')[0] != 'rok vydání':
                        detail_data['rok2'].append(np.nan)
                except:
                    detail_data['rok2'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split('\n')[0] == 'vydání':
                        detail_data['vydani0'].append(soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split('\n')[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split('\n')[0] != 'vydání':
                        detail_data['vydani0'].append(np.nan)
                except:
                    detail_data['vydani0'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n')[0] == 'vydání':
                        detail_data['vydani1'].append(soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n')[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n')[0] != 'vydání':
                        detail_data['vydani1'].append(np.nan)
                except:
                    detail_data['vydani1'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[3].text.strip().split('\n')[0] == 'vydání':
                        detail_data['vydani2'].append(soup.find('table', class_='table table-striped').find_all('tr')[3].text.strip().split('\n')[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[3].text.strip().split('\n')[0] != 'vydání':
                        detail_data['vydani2'].append(np.nan)
                except:
                    detail_data['vydani2'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] == 'jazyk':
                        detail_data['jazyk0'].append(soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[1].replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', ''))
                    if soup.find('table', class_='table table-striped').find_all('tr')[2].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] != 'jazyk':
                        detail_data['jazyk0'].append(np.nan)
                except:
                        detail_data['jazyk0'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[3].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] == 'jazyk':
                        detail_data['jazyk1'].append(soup.find('table', class_='table table-striped').find_all('tr')[3].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[1].replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', ''))
                    if soup.find('table', class_='table table-striped').find_all('tr')[3].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] != 'jazyk':
                        detail_data['jazyk1'].append(np.nan)
                except:
                        detail_data['jazyk1'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] == 'jazyk':
                        detail_data['jazyk2'].append(soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[1].replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', ''))
                    if soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] != 'jazyk':
                        detail_data['jazyk2'].append(np.nan)
                except:
                        detail_data['jazyk2'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[5].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] == 'jazyk':
                        detail_data['jazyk3'].append(soup.find('table', class_='table table-striped').find_all('tr')[5].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[1].replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', ''))
                    if soup.find('table', class_='table table-striped').find_all('tr')[5].text.strip().split('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')[0] != 'jazyk':
                        detail_data['jazyk3'].append(np.nan)
                except:
                        detail_data['jazyk3'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn0'].append(soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[4].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn0'].append(np.nan)
                except:
                    detail_data['isbn0'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[5].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn'].append(soup.find('table', class_='table table-striped').find_all('tr')[5].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[5].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn'].append(np.nan)
                except:
                    detail_data['isbn'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[6].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn1'].append(soup.find('table', class_='table table-striped').find_all('tr')[6].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[6].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn1'].append(np.nan)
                except:
                    detail_data['isbn1'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[7].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn2'].append(soup.find('table', class_='table table-striped').find_all('tr')[7].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[7].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn2'].append(np.nan)
                except:
                    detail_data['isbn2'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[8].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn3'].append(soup.find('table', class_='table table-striped').find_all('tr')[8].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[8].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn3'].append(np.nan)
                except:
                    detail_data['isbn3'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[9].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn4'].append(soup.find('table', class_='table table-striped').find_all('tr')[9].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[9].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn4'].append(np.nan)
                except:
                    detail_data['isbn4'].append(np.nan)
                try:
                    if soup.find('table', class_='table table-striped').find_all('tr')[10].text.strip().split()[0] == 'ISBN':
                        detail_data['isbn5'].append(soup.find('table', class_='table table-striped').find_all('tr')[10].text.strip().split()[1])
                    if soup.find('table', class_='table table-striped').find_all('tr')[10].text.strip().split()[0] != 'ISBN':
                        detail_data['isbn5'].append(np.nan)
                except:
                    detail_data['isbn5'].append(np.nan)
        return detail_data
    
    