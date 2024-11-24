# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import TextResponse
from itemadapter import is_item, ItemAdapter
import logging

class Amazon2SpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        # Create an instance of the middleware and connect it to the signals
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response before it is passed to the spider.
        return None

    def process_spider_output(self, response, result, spider):
        # Process the results returned from the spider and return them.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Handle exceptions raised during spider processing (e.g., network issues, etc.)
        spider.logger.error(f"Exception occurred: {exception}")
        # Optionally retry or handle specific exceptions
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider.
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class Amazon2DownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        # Create an instance of the middleware and connect it to the signals
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader middleware.
        return None

    def process_response(self, request, response, spider):
        # Check if the response is text and handle CAPTCHA or blocked pages
        if isinstance(response, TextResponse):
            if self.is_banned(response):
                spider.logger.info("Blocked response detected, retrying...")
                # Here you can handle CAPTCHA pages or blocked requests (e.g., use a new proxy, retry, etc.)
                # For example, you could create a new request to retry with a different proxy:
                # return scrapy.Request(url=request.url, dont_filter=True, callback=spider.parse)
            else:
                return response
        else:
            spider.logger.warning(f"Non-text response received: {response.status} {response.url}")
            return response

    def process_exception(self, request, exception, spider):
        # Handle exceptions raised during the request processing (e.g., network errors).
        spider.logger.error(f"Exception occurred while downloading {request.url}: {exception}")
        pass

    def is_banned(self, response):
        # Implement logic to detect if the response indicates a CAPTCHA or ban.
        # This could be checking for specific text patterns, status codes, or CAPTCHA forms.
        banned_patterns = [r"captcha", r"robot", r"blocked"]
        if any(pattern.lower() in response.text.lower() for pattern in banned_patterns):
            return True
        return False

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")
