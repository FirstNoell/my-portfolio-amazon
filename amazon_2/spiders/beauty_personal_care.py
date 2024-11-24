import scrapy
from scrapy_splash import SplashRequest
from datetime import datetime

class BeautyPersonalCareSpider(scrapy.Spider):
    name = "beauty_personal_care"
    allowed_domains = ["amazon.com"]
    start_urls = ["https://www.amazon.com"]

    lua_script = '''
    function main(splash, args)
        splash.private_mode_enabled = false
        splash:set_viewport_full()

        local ok, reason = splash:go(args.url)
        if not ok then
            return {error = "Failed to load URL: " .. reason}
        end
        splash:wait(2)

        local input_box = splash:select("#twotabsearchtextbox")
        if not input_box then
            return {error = "Search box not found"}
        end
        input_box:focus()
        input_box:send_text("Beauty & Personal Care")
        splash:wait(1)

        local button = splash:select("#nav-search-submit-button")
        if not button then
            return {error = "Search button not found"}
        end
        button:mouse_click()
        splash:wait(5)

        return {
            html = splash:html(),
            png = splash:png(),
        }
    end
    '''

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint="execute",
                args={"lua_source": self.lua_script, "timeout": 90},
                dont_filter=True
            )

    def parse(self, response):
        if 'text/html' in response.headers.get('Content-Type', '').decode():
            self.log("Received HTML response")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"response_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(response.text)

            products = response.xpath(
                '//div[contains(@class, "s-main-slot")]//div[contains(@data-component-type, "s-search-result")]'
            )

            for product in products:
                yield {
                    'Title': product.xpath('.//span[@class="a-size-base-plus a-color-base a-text-normal"]/text()').get(default='N/A'),
                    'Ratings': product.xpath('.//span[@class="a-icon-alt"]/text()').get(default='No ratings'),
                    'Price': product.xpath('.//span[contains(@class, "a-price-whole")]/text()').get(default='Price not available'),
                    'Image': product.xpath('.//img[contains(@class, "s-image")]/@src').get(default='No image URL'),
                }

            next_page = response.xpath('//a[contains(@aria-label, "Next")]/@href').get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                yield SplashRequest(
                    next_page_url,
                    callback=self.parse_next_page,
                    endpoint="execute",
                    args={"lua_source": self.lua_script, "timeout": 90, "wait": 5},
                    dont_filter=True
                )
            else:
                self.log("No more pages to scrape.")
        else:
            self.log("Received non-HTML response, skipping parsing.")

    def parse_next_page(self, response):
        if 'text/html' in response.headers.get('Content-Type', '').decode():
            self.log("Received HTML response on next page")
            products = response.xpath(
                '//div[contains(@class, "s-main-slot")]//div[contains(@data-component-type, "s-search-result")]'
            )

            for product in products:
                yield {
                    'Title': product.xpath('.//span[@class="a-size-base-plus a-color-base a-text-normal"]/text()').get(default='N/A'),
                    'Ratings': product.xpath('.//span[@class="a-icon-alt"]/text()').get(default='No ratings'),
                    'Price': product.xpath('.//span[contains(@class, "a-price-whole")]/text()').get(default='Price not available'),
                    'Image': product.xpath('.//img[contains(@class, "s-image")]/@src').get(default='No image URL'),
                }

            next_page = response.xpath('//a[contains(@aria-label, "Next")]/@href').get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                yield SplashRequest(
                    next_page_url,
                    callback=self.parse_next_page,
                    endpoint="execute",
                    args={"lua_source": self.lua_script, "timeout": 90},
                    dont_filter=True
                )
            else:
                self.log("No more pages to scrape.")
        else:
            self.log("Received non-HTML response on next page, skipping parsing.")
