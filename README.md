### README.md

# Async Web Scraper with Rotating Proxies

This project demonstrates an asynchronous web scraper implemented in Python using the `aiohttp` library. The scraper is designed to rotate between multiple proxy servers and user-agent headers to avoid IP blocking and scraping restrictions.

## Features

- Asynchronous web scraping with `aiohttp`.
- Rotating proxies using `aiohttp-socks`.
- Randomly rotating user-agent headers.
- Logging with `logging` module.
- Configuration management with `dotenv`.
- Proxy testing before scraping.

## Requirements

- Python 3.8 or higher
- `aiohttp`
- `aiohttp-socks`
- `beautifulsoup4`
- `pandas`
- `python-dotenv`
- `rich`
- `requests`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/peterkacmarik/async-scrape-trhknih.git
   cd async-scrape-trhknih
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory and add the following environment variables:
   ```plaintext
   LOG_DIR_MAIN=path/to/your/logfile.log
   ```

5. Update the `config.json` file with the appropriate scraping settings:
   ```json
   {
       "scraping_settings": {
           "base_url_nabidky": "http://example.com/page",
           "user_agents": [
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
               "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
               "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
           ]
       }
   }
   ```

## Usage

1. Create a list of URLs to scrape:
   ```python
   start_page = 1
   end_page = 2
   base_url_nabidky = load_settings()['scraping_settings']['base_url_nabidky']
   urls = [f'{base_url_nabidky}{page}' for page in range(start_page, end_page + 1)]
   ```

2. Load the proxy list and user-agent headers:
   ```python
   proxy_list = get_proxy()
   user_agents = load_settings()['scraping_settings']['user_agents']
   ```

3. Initialize the `ResponseScraper` object and start the scraping process:
   ```python
   response_scraper = ResponseScraper(urls, proxy_list, user_agents)
   pages_responses = asyncio.run(response_scraper.main())
   ```

4. Process the scraped data using `BeautifulSoup` and `pandas`:
   ```python
   data_scraper = DataScraper(pages_responses)
   results_all_urls = data_scraper.get_url()
   df = pd.DataFrame(result_detail_data)
   df.to_csv('async-scrape-trhknih/trhknih.csv', index=False, encoding='utf-8-sig')
   ```

## Code Example

Here's a complete example of the `ResponseScraper` class and how to use it:

```python
import aiohttp
import asyncio
import random
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
from typing import List
import logging
from datetime import datetime
import pandas as pd

class ResponseScraper:
    def __init__(self, urls: List[str], proxy_list: List[str], user_agents: List[str]) -> None:
        self.urls = urls
        self.proxy_list = proxy_list
        self.user_agents = user_agents
        self.one_page_response = None
        self.list_all_responses = []

    async def fetch(self, url: str, session: aiohttp.ClientSession):
        headers = {"User-Agent": random.choice(self.user_agents)}
        try:
            async with session.get(url=url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    self.one_page_response = await response.text()
                    return self.one_page_response
                else:
                    logging.error(f"Request failed: {response.status}, message='{response.reason}', url={response.url}")
                    return None
        except Exception as e:
            logging.error(f"Request failed: {e}")
            return None

    async def fetch_all_pages(self):
        task_responses = []
        connector = ProxyConnector.from_url(random.choice(self.proxy_list))
        async with aiohttp.ClientSession(connector=connector) as session:
            for url in self.urls:
                task_response = asyncio.create_task(self.fetch(url, session))
                task_responses.append(task_response)
            self.list_all_responses = await asyncio.gather(*task_responses)
        return self.list_all_responses

    async def main(self):
        await self.test_proxies()
        pages_responses = await self.fetch_all_pages()
        return pages_responses

if __name__ == "__main__":
    start_page = 1
    end_page = 2
    base_url_nabidky = "http://example.com/page"
    urls = [f'{base_url_nabidky}{page}' for page in range(start_page, end_page + 1)]
    proxy_list = [
        'http://154.16.16.20:80',
        'http://89.35.237.187:4153',
        'http://181.198.53.6:3128'
    ]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ]

    response_scraper = ResponseScraper(urls, proxy_list, user_agents)
    pages_responses = asyncio.run(response_scraper.main())

    if not pages_responses:
        print("No pages to scrape.")
    else:
        data_scraper = DataScraper(pages_responses)
        results_all_urls = data_scraper.get_url()
        df = pd.DataFrame(results_all_urls)
        df.to_csv('async-scrape-trhknih/trhknih.csv', index=False, encoding='utf-8-sig')
```

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

- [aiohttp](https://github.com/aio-libs/aiohttp)
- [aiohttp-socks](https://github.com/romis2012/aiohttp-socks)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [pandas](https://pandas.pydata.org/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [rich](https://github.com/Textualize/rich)

---

This `README.md` file provides a comprehensive guide on how to set up and use the asynchronous web scraper with rotating proxies. It includes installation instructions, a usage example, and information about the project features and dependencies.
