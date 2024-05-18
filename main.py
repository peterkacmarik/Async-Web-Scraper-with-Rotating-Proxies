from typing import List
from aiohttp_socks import ProxyConnector
import pandas as pd
import random
from datetime import datetime
import asyncio
import aiohttp
from proxy import get_working_proxies, get_proxy
from rich import print
from scraper import DataScraper
from dotenv import load_dotenv
import os
import logging
from logs import logger
from config import load_settings


# Load environment variables
load_dotenv()

# Load logger settings from .env file
LOG_DIR_MAIN = os.getenv('LOG_DIR_MAIN')

# Create logger object
logger = logger.get_logger(log_file=LOG_DIR_MAIN, log_level=logging.INFO)


class ResponseScraper:
    def __init__(self, urls: List, proxy_list: List, user_agents: List) -> None:
        """
        Initializes the ResponseScraper class with the given URLs, proxy list, and user agents.

        Parameters:
            urls (List[str]): A list of URLs to scrape.
            proxy_list (List[str]): A list of proxies to use for the scraping.
            user_agents (List[str]): A list of user agents to use for the scraping.

        Returns:
            None
        """
        self.urls = urls
        self.proxy_list = proxy_list
        self.user_agents = user_agents
        self.one_page_response = None
        self.list_all_responses = []
        self.working_proxies = []

    async def fetch(self, url: str, session: aiohttp.ClientSession):
        """
        Asynchronously fetches a web page from the given URL using the provided session and proxy.

        Args:
            url (str): The URL of the web page to fetch.
            session (aiohttp.ClientSession): The aiohttp client session to use for the request.
            proxy (str): The proxy to use for the request.

        Returns:
            str or None: The content of the fetched web page as a string, or None if the request failed.
        """
        headers: dict = {"User-Agent": random.choice(self.user_agents)} # generate random user agent
        try:
            # logger.info(f"Requesting: {url}")
            async with session.get(url=url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    logger.info(f"Request successful: {url} - {response.status}")
                    self.one_page_response = await response.text()
                    return self.one_page_response
                else:
                    logger.error(f"Request failed: {response.status}, message='{response.reason}', proxy_url={response.url}")
                    return None
        except Exception as e:
            logger.error(f"Error: Request failed: {e}")
            return None
        
    async def fetch_all_pages(self) -> List[str]:
        """
        Fetches all pages using available proxies.

        Returns:
            A list of HTML responses from all pages.
        """
        task_responses: List[asyncio.Task] = []
        
        # Create a ProxyConnector with random proxy from proxy_list
        connector = ProxyConnector.from_url(random.choice(self.working_proxies))
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for url in self.urls:
                task_response = asyncio.create_task(self.fetch(url, session))
                task_responses.append(task_response)
            self.list_all_responses = await asyncio.gather(*task_responses)
        return self.list_all_responses

    async def test_proxies(self):
        self.working_proxies: List = await get_working_proxies(self.proxy_list)
    
    async def main(self):
        """
        Main function to test proxies and fetch all pages.
        """
        await self.test_proxies()  # Test proxy servers before scraping
        proxies_count: int = len(self.working_proxies)
        if not proxies_count:
            logger.info("No working proxies found.")
            return []
        else:
            logger.info(f"Found {proxies_count} working proxies.")
            pages_responses: List = await self.fetch_all_pages()
            logger.info(f"Total number of pages: {len(pages_responses)}")
            return pages_responses


if __name__ == "__main__":
    # Create a list of URLs
    start_page: int = 1
    end_page: int = 2
    base_url_nabidky: str = load_settings()['scraping_settings']['base_url_nabidky']
    urls: List = [f'{base_url_nabidky}{page}' for page in range(start_page, end_page + 1)]
    
    # List of proxies from file
    proxy_list: List = get_proxy()
    
    # List of User-Agents headers
    user_agents: List = load_settings()['scraping_settings']['user_agents']
    
    # Start time for responses
    start_time_responses: datetime = datetime.now()
    
    # Create a ResponseScraper object with the list of URLs and proxies and user agents
    response_scraper_urls: ResponseScraper = ResponseScraper(urls, proxy_list, user_agents)
    
    # Create a list of responses
    pages_responses: List = asyncio.run(response_scraper_urls.main())
    
    # End time for responses
    end_time_responses: datetime = datetime.now()
    logger.info(f'Elapsed time for responses: {end_time_responses - start_time_responses} seconds')
    
    # Number of responses in list of responses
    num_responses: int = len(pages_responses)

    # Counting responses that are None
    count_none: int = sum(1 for response in pages_responses if response is None)
    if count_none == num_responses:
        print("No pages to scrape.")
        exit()

    else:
        # Start time for urls
        start_time_urls: datetime = datetime.now()
        
        # Create a DataScraper object with the list of responses
        results_all_urls: List = DataScraper(pages_responses).get_url()
        
        # End time for urls
        end_time_urls: datetime = datetime.now()
        logger.info(f'Elapsed time for urls: {end_time_urls - start_time_urls} seconds')

        # Start time for details
        start_time_details: datetime = datetime.now()
        
        # Create a ResponseScraper object with the list of urls and proxies and user agents
        response_scraper_details: ResponseScraper = ResponseScraper(results_all_urls, proxy_list, user_agents)
        
        # Create a list of responses
        all_responses_details: List = asyncio.run(response_scraper_details.main())

        # Create a DataScraper object with the list of details
        result_detail_data: List = DataScraper(all_responses_details).get_url_details()

        # End time for details
        end_time_details: datetime = datetime.now()
        logger.info(f'Elapsed time for details: {end_time_details - start_time_details} seconds')
        
        # Create DataFrame
        df: pd.DataFrame = pd.DataFrame(result_detail_data)
        
        # Clean DataFrame data
        df['ISBN'] = df['isbn'].fillna('') + ' ' + df['isbn0'].fillna('') + ' ' + df['isbn1'].fillna('') + ' ' + df['isbn2'].fillna('') + ' ' + df['isbn3'].fillna('') + ' ' + df['isbn4'].fillna('') + ' ' + df['isbn5'].fillna('')
        df['rok'] = df['rok1'].fillna('') + ' ' + df['rok2'].fillna('')
        df['vydani'] = df['vydani0'].fillna('') + ' ' + df['vydani1'].fillna('') + ' ' + df['vydani2'].fillna('')
        df['jazyk'] = df['jazyk0'].fillna('') + ' ' + df['jazyk1'].fillna('') + ' ' + df['jazyk2'].fillna('') + ' ' + df['jazyk3'].fillna('')
        
        # Drop columns that are not needed for the analysis
        df: pd.DataFrame = df.drop(columns=['rok1', 'rok2', 'isbn', 'isbn0', 'isbn1', 'isbn2', 'isbn3', 'isbn4', 'isbn5', 'vydani0', 'vydani1', 'vydani2', 'jazyk0', 'jazyk1', 'jazyk2', 'jazyk3'])

        # Print DataFrame to console
        print(df)
        
        # Save DataFrame to CSV file
        # df.to_csv('async-scrape-trhknih/trhknih.csv', index=False, encoding='utf-8-sig')

