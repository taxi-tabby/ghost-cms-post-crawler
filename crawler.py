import requests
from requests.exceptions import RequestException
import time
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, timeout=10, max_retries=3, retry_delay=2):
        """
        Initialize the WebCrawler with configurable parameters.
        
        Args:
            timeout (int): Request timeout in seconds
            max_retries (int): Number of retry attempts
            retry_delay (int): Delay between retries in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Default headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def get_page_content(self, url):
        """
        Retrieve the HTML body content from the specified URL.
        
        Args:
            url (str): The URL to crawl
            
        Returns:
            str: HTML content of the page body or empty string if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                # Check if request was successful
                if response.status_code == 200:
                    return response.text
                
                # If we get a rate limit or temporary failure, try again after delay
                if response.status_code in (429, 503, 504):
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                # Other failure status codes
                return ""
                
            except RequestException:
                # Wait before retrying
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                continue
            except Exception:
                # Catch any other exceptions
                return ""
        
        # If we've exhausted all retries
        return ""
    
    def set_headers(self, headers):
        """
        Set custom headers for requests.
        
        Args:
            headers (dict): Dictionary containing header key-value pairs
        """
        self.headers = headers
        
    def extract_links(self, url, css_selectors):
        """
        Extract links from a webpage based on provided CSS selectors.
        
        Args:
            url (str): URL to crawl
            css_selectors (list[str]): List of CSS selectors to target
            
        Returns:
            list: List of extracted href URLs
        """
        # Get the page content
        html_content = self.get_page_content(url)
        
        if not html_content:
            return []
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract links from each selector
        links = []
        for selector in css_selectors:
            # Find elements matching the selector
            elements = soup.select(selector)
            
            # Extract all anchor tags from these elements
            for element in elements:
                anchors = element.find_all('a')
                for anchor in anchors:
                    href = anchor.get('href')
                    if href:
                        # Add to our links list if it's not already there
                        if href not in links:
                            links.append(href)
        
        return links
    
