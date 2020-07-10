import scrapy


class ProductSpider(scrapy.Spider):
    name = 'products'

    start_urls = [
        "https://ezakupy.tesco.pl/groceries/pl-PL/"
    ]

    def make_category_url(self, resp, cat):
        cat_str = cat.xpath(""".//@href""").extract_first()
        cat_url = cat_str[:cat_str.index('?')] + '/all'
        return resp.urljoin(cat_url)

    def parse(self, resp):
        for category in resp.xpath("""//div[@class='menu-tree__inner']/ul/li/a"""):
            yield scrapy.Request(url=self.make_category_url(resp, category), callback=self.parse_products)

    def parse_products(self, resp):
        for product in resp.xpath("""//div[@class='tile-content']"""):
            yield {
                'name': product.xpath(""".//div[@class='product-details--content']/h3/a/text()""").extract_first(),
                'img': product.xpath(""".//div[@class='product-image__container']/img/@src""").extract_first(),
                'single-price': product.xpath(""".//span[@class='value']/text()""").extract()[0],
                'price-per-unit': product.xpath(""".//span[@class='value']/text()""").extract()[1],
                'unit': product.xpath(""".//span[@class='weight']/text()""").extract_first()[1:]
            }

        next_page = resp.xpath(
            """//a[descendant::span[@class='icon-icon_whitechevronright']]/@href""").extract_first()
        if next_page is not None:
            next_page_link = resp.urljoin(next_page)
            yield scrapy.Request(url=next_page_link, callback=self.parse_products)
