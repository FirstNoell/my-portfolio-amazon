import scrapy
import json  # Import the json module
from scrapy_splash import SplashRequest

class RedditSpider(scrapy.Spider):
    name = 'reddit_spider'
    allowed_domains = ['reddit.com', 'localhost']
    start_urls = ['https://www.reddit.com/r/all/new.json']  # API endpoint for latest posts

    def start_requests(self):
        # Define custom headers with User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'application/json',  # Ensuring we accept JSON
        }

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=headers)  # Directly request JSON

    def parse(self, response):
        self.logger.info(f"Response status: {response.status}")

        # Access the JSON data directly from response
        try:
            json_data = json.loads(response.text)  # Load the response text as JSON
        except Exception as e:
            self.logger.error(f"Error parsing JSON: {e}")
            return

        # Navigate the JSON structure to find posts
        posts = json_data.get('data', {}).get('children', [])

        if not posts:
            self.logger.warning("No posts found.")
            return

        for post in posts:
            yield {
                'title': post['data'].get('title', 'No title'),
                'username': post['data'].get('author', 'Unknown'),
                'post_time': post['data'].get('created_utc', 'No time')  # This will return a UNIX timestamp
            }
