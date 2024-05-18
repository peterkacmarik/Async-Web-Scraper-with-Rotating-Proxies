import logging
import requests
import random
import os
import csv
from datetime import datetime
from logs import logger
from dotenv import load_dotenv
from rich import print
from config import load_settings
import aiohttp
import asyncio
import random


# Load environment variables
load_dotenv()

# Load logger settings from .env file
LOG_DIR_PROXIES = os.getenv('LOG_DIR_PROXIES')

# Create logger object
logger = logger.get_logger(log_file=LOG_DIR_PROXIES, log_level=logging.INFO)


def get_proxy():
    """
    Reads a list of proxies from a CSV file and returns a random sample of 10 proxies.

    This function opens the 'proxy_list.csv' file located in the 'async-scrape-trhknih/proxy' directory.
    It reads the contents of the file using the `csv.reader` function and creates a list of proxies by
    prepending 'http://' to each row in the file. Finally, it returns a random sample of 10 proxies
    from the list using the `random.sample` function.

    Returns:
        list: A random sample of 10 proxies.

    Raises:
        FileNotFoundError: If the 'proxy_list.csv' file does not exist.
        ValueError: If the proxy list is empty.
    """
    # Load proxy list from path in settings
    proxy_list_path = load_settings()['proxy_settings']['proxy_list1']
    
    # Read proxy list from file
    with open(proxy_list_path, 'r') as file:
        reader: csv.reader = csv.reader(file)
        proxy_list: list = ['http://' + row[0] for row in reader]
        return random.sample(proxy_list, k=10)

async def test_proxy(proxy: str):
    """
    Asynchronously tests a proxy by making a GET request to a public endpoint that returns an IP address.

    Args:
        proxy (str): The proxy to test.

    Returns:
        str or None: The working proxy if the request is successful, None otherwise.

    Raises:
        Exception: If an error occurs during the request.

    Notes:
        - The public endpoint used for testing is "http://httpbin.org/ip".
        - SSL verification is turned off for testing purposes.
        - The function logs the working proxy and any errors encountered.
    """
    # Load path from config file
    url: str = load_settings()['proxy_settings']['proxy_check_url']  # You can use any public endpoint that returns an IP
    try:
        connector: aiohttp.BaseConnector = aiohttp.TCPConnector(ssl=False, limit=100)  # Turn off SSL verification for testing
        async with aiohttp.ClientSession(connector=connector) as session:
            # logger.info(f"Testing proxy: {proxy}")
            async with session.get(url=url, proxy=proxy, timeout=10) as response:
                if response.status == 200:
                    logger.info(f"Proxy {proxy} working")
                    return proxy
    except Exception as e:
        logger.error(f"Proxy {proxy} failed: {e}")
    return None

async def get_working_proxies(proxy_list: list):
    """
    Asynchronously tests a list of proxies and returns a list of working proxies.

    Args:
        proxy_list (List[str]): A list of proxies to test.

    Returns:
        List[str]: A list of working proxies.

    Raises:
        None
    """
    # Test each proxy in parallel using asyncio gathering method
    tasks: list = [test_proxy(proxy) for proxy in proxy_list]
    
    # Wait for all tasks to complete
    working_proxies: list = await asyncio.gather(*tasks)
    
    # Remove None values from the list and return it
    return [proxy for proxy in working_proxies if proxy is not None]


# Function to get proxy list from API and return list of proxies
# def get_proxy_list_from_api():
#     """
#     Retrieves a list of proxies from the ProxyScrape API.

#     This function sends a GET request to the ProxyScrape API to retrieve a list of free proxies.
#     The API URL is constructed with the following parameters:
#     - request: getproxies
#     - skip: 0
#     - proxy_format: protocolipport
#     - format: json
#     - limit: 7 (number of proxies to retrieve at once)

#     The function includes a set of headers to mimic a browser request.

#     Returns:
#         list: A list of proxies in the format 'protocol://ip:port'.
#             The protocol is either 'http' or 'https'.

#     Raises:
#         requests.exceptions.RequestException: If there is an error with the request.
#     """
#     url: str = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&skip=0&proxy_format=protocolipport&format=json&limit=7"  # limit=20 = 20 proxies at once 

#     headers: dict = {
#     'accept': 'application/json, text/plain, */*',
#     'accept-language': 'sk-SK,sk;q=0.9,cs;q=0.8,en-US;q=0.7,en;q=0.6',
#     'origin': 'https://proxyscrape.com',
#     'priority': 'u=1, i',
#     'referer': 'https://proxyscrape.com/',
#     'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
#     }
    
#     response: requests.models.Response = requests.request("GET", url, headers=headers)
#     json_data: dict = response.json()
#     start_point: list = json_data['proxies']

#     list_proxies: list = []
#     for point in start_point:
#         # proxies: str = f'{point["ip"]}:{point["port"]}'
#         if point['protocol'] == 'http':
#             list_proxies.append(point['proxy'])
#         elif point['protocol'] == 'https':
#             list_proxies.append(point["proxy"])
#     return list_proxies


# Function to check availability of proxies and return list of available proxies
# def check_proxies(proxies: list):
#     """
#     Check the availability of a list of proxies and return a list of available proxies.

#     Parameters:
#     - proxies (list): A list of proxy addresses to check.

#     Raises:
#     - ValueError: If the proxy list is empty.
#     - ValueError: If the proxy check URL is empty.

#     Returns:
#     - list: A list of available proxy addresses.

#     Note:
#     - This function makes use of the `requests` library to send HTTP requests.
#     - The function logs any errors or information related to the proxy availability.
#     - The function measures the total time taken to check all proxies.
#     """
#     if proxies is None:
#         raise ValueError('Proxy list is empty')

#     proxy_check_url: str = load_settings()['proxy_settings']['proxy_check_url']
#     if proxy_check_url is None:
#         raise ValueError('Proxy check URL is empty')

#     start_time = datetime.now()
    
#     available_proxies = []
#     print(f'\n\t*** Number proxies to check: {len(proxies)} ***')
#     for index, proxy in enumerate(proxies, start=1):
#         if proxy is None:
#             raise ValueError('Proxy is null')
#         try:
#             response: requests.models.Response = requests.get(proxy_check_url, proxies={"http": proxy, "https": proxy}, timeout=3)
#             if response is None:
#                 logger.error(f'Proxy {index} :: {proxy}  --  Null Response')
#             elif response.status_code == 200:
#                 logger.info(f'Proxy {index} :: {proxy}  --  Available')
#                 available_proxies.append(proxy)
#             else:
#                 logger.info(f'Proxy {index} :: {proxy}  --  Not Available ({response.status_code})')
#         except requests.exceptions.ConnectTimeout as e:
#             logger.error(f'Proxy {index} :: {proxy}  --  Connect Timeout')
#         except requests.exceptions.ConnectionError as e:
#             logger.error(f'Proxy {index} :: {proxy}  --  Connection Error')
#         except requests.exceptions.InvalidURL as e:
#             logger.error(f'Proxy {index} :: {proxy}  --  Invalid URL')
#         # except requests.exceptions.ProxyError as e:
#         #     logger.error(f'Proxy {index} :: {proxy}  --  Proxy Error')
#         # except requests.exceptions.SSLError as e:
#         #     logger.error(f'Proxy {index} :: {proxy}  --  SSL Error')
#         except requests.exceptions.Timeout as e:
#             logger.error(f'Proxy {index} :: {proxy}  --  Timeout')
#         except requests.exceptions.TooManyRedirects as e:
#             logger.error(f'Proxy {index} :: {proxy}  --  Too Many Redirects')
#         except Exception as e:
#             logger.error(f'Proxy {index} :: {proxy}  --  Unhandled Exception: {e}')

#     end_time = datetime.now()
#     logger.info(f'Total time to check all proxies: {end_time - start_time}')
#     logger.info(f'Total available proxies for scraping: {len(available_proxies)}\n')
#     return available_proxies



# list_proxy = get_proxy_list_from_api()
# available_proxy = check_proxies(list_proxy)
# print(available_proxy)