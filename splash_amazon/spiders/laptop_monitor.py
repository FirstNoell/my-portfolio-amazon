import scrapy
from scrapy_splash import SplashRequest

class LaptopMonitorSpider(scrapy.Spider):
    name = "laptop_monitor"
    allowed_domains = ["amazon.com", "localhost"]

    script = '''
        function main(splash, args)
          assert(splash:go(args.url))
          assert(splash:wait(2))

          local input_box = assert(splash:select("#twotabsearchtextbox"))
          input_box:focus()
          input_box:send_text("laptop monitor extender 15")
          assert(splash:wait(2))

          local button = assert(splash:select("#nav-search-submit-button"))
          button:mouse_click()
          assert(splash:wait(5))  

          return {
            html = splash:html(),
            png = splash:png(),
            har = splash:har(),
          }
        end
    '''

    def start_requests(self):
        yield SplashRequest(
            url='https://www.amazon.com/s?k=laptop+monitor+extender+15',
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.script}
        )

    def parse(self, response):
        self.logger.info("Response URL: %s", response.url)
        self.logger.info("Response status: %s", response.status)

        for product in response.css('div.s-main-slot div.s-result-item'):
            title = product.css('span.a-size-medium.a-color-base.a-text-normal::text').get()
            price_whole = product.css('span.a-price-whole::text').get()
            price_decimal = product.css('span.a-price-fraction::text').get()
            price = f"{price_whole}.{price_decimal}" if price_whole and price_decimal else None
            link = product.css('a.a-link-normal.s-link-style::attr(href)').get()

            yield {
                'title': title,
                'price': price,
                'link': response.urljoin(link),
            }

        # Handle pagination
        next_page = response.css('a.s-pagination-next::attr(href)').get()
        if next_page:
            # Make sure to join the next_page with the base URL
            next_page_url = response.urljoin(next_page)
            self.logger.info("Next page URL: %s", next_page_url)  # Log the next page URL
            yield SplashRequest(
                url=next_page_url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.script}
            )
