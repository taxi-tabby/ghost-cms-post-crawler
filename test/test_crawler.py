import pytest
import requests
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler import WebCrawler


@pytest.fixture
def crawler():
    """Return a WebCrawler instance with default settings."""
    return WebCrawler()

@pytest.fixture
def custom_crawler():
    """Return a WebCrawler instance with custom settings."""
    return WebCrawler(timeout=5, max_retries=2, retry_delay=1)




class TestWebCrawler:
    
    
    
    def test_init(self, crawler, custom_crawler):
        """기본 초기화 테스트"""
        
        
        
        # 크라울러 기본 값 체크
        assert crawler.timeout == 10
        assert crawler.max_retries == 3
        assert crawler.retry_delay == 2
        
        # 기본값을 바꾼 크라울러 값 체크
        assert custom_crawler.timeout == 5
        assert custom_crawler.max_retries == 2
        assert custom_crawler.retry_delay == 1
        
        # 기본 해더 값 체크
        assert 'User-Agent' in crawler.headers
        assert 'Accept' in crawler.headers
        assert 'Accept-Language' in crawler.headers
    
    
    def test_set_headers(self, crawler):
        """해더 설정 기능 테스트"""
        custom_headers = {'User-Agent': 'Test Agent', 'Custom-Header': 'Value'}
        crawler.set_headers(custom_headers)
        
        assert crawler.headers == custom_headers
        assert crawler.headers['User-Agent'] == 'Test Agent'
        assert crawler.headers['Custom-Header'] == 'Value'
    
    
    @patch('requests.get')
    def test_get_page_content_success(self, mock_get, crawler):
        """페이지 요청 기능 테스트"""


        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test Page</body></html>"
        mock_get.return_value = mock_response
        

        result = crawler.get_page_content("http://example.com")
        assert result == "<html><body>Test Page</body></html>"
        
        mock_get.assert_called_once_with(
            "http://example.com",
            headers=crawler.headers,
            timeout=crawler.timeout
        )

        
        
        
    @patch.object(WebCrawler, 'get_page_content')
    def test_extract_links_empty_response(self, mock_get_page_content, crawler):
        """목록 추출 시 빈 응답에 대한 예외 테스트"""
        mock_get_page_content.return_value = ""
        
        links = crawler.extract_links("https://blog.smallbrain-labo.work", ['.nav li'])
        assert links == []



    @patch.object(WebCrawler, 'get_page_content')
    def test_extract_links(self, mock_get_page_content, crawler):
        """목록 추출 기능 테스트"""
        
        html = """
        <html>
            <body>
                <div class="menu">
                    <a href="/page1">Page 1</a>
                    <a href="/page2">Page 2</a>
                </div>
                <div class="content">
                    <a href="/page3">Page 3</a>
                </div>
            </body>
        </html>
        """
        mock_get_page_content.return_value = html
        

        links = crawler.extract_links("https://blog.smallbrain-labo.work", ['.menu', '.content'])

        assert len(links) == 3
        assert "/page1" in links
        assert "/page2" in links
        assert "/page3" in links
