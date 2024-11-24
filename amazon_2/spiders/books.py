import scrapy
from scrapy_splash import SplashRequest

class AmazonSearchSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://www.amazon.com/"]

    # Lua script for searching "best sellers books 2024"
    lua_script = """
    function main(splash, args)
        splash.private_mode_enabled = false
        splash:set_viewport_full()

        -- Navigate to the URL
        assert(splash:go(args.url))
        assert(splash:wait(2))

        -- Select the search box and type "best sellers books 2024"
        local input_box = assert(splash:select("#twotabsearchtextbox"))
        input_box:focus()
        input_box:send_text("best sellers books 2024")  -- Corrected: just send the search term
        assert(splash:wait(1))

        -- Click the search button
        local button = assert(splash:select("#nav-search-submit-button"))
        button:mouse_click()
        assert(splash:wait(5))

        -- Return HTML and a screenshot for debugging
        return {
            html = splash:html(),
            png = splash:png(),
        }
    end
    """

    # Add a page counter
    page_counter = 1

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint="execute",
                args={"lua_source": self.lua_script, "timeout": 90, "wait": 5},  # Lua script included here
                headers={
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                },
            )

    def parse(self, response):
        # Parse Amazon search results page for books
        books = response.xpath(
            '//div[contains(@class, "s-main-slot")]//div[contains(@data-component-type, "s-search-result")]'
        )
        for book in books:
            yield {
                "Title": book.xpath('.//span[@class="a-size-base-plus a-color-base a-text-normal"]/text()').get(),
                "Author": book.xpath(
                    './/a[@class="a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style"]/text()'
                ).get(),
                "Ratings": book.xpath('.//span[@class="a-icon-alt"]/text()').get(),
                "Price": book.xpath('.//span[contains(@class, "a-price")]//span[@class="a-price-whole"]/text()').get(),
                "Link": response.urljoin(book.xpath('.//h2/a/@href').get()),
            }

        # Handle pagination: Stop after page 10
        current_page = response.meta.get("page", 1)
        if current_page < 10:
            next_page = response.xpath('//a[contains(@aria-label, "Next")]/@href').get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                yield SplashRequest(
                    next_page_url,
                    self.parse,
                    endpoint="execute",
                    args={"lua_source": self.lua_script, "timeout": 90, "wait": 5},  # Lua script included here
                    meta={"page": current_page + 1},  # Increment page counter
                    headers={
                        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                    },
                )
