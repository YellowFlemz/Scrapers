import re
import scrapy
from scraper.items import AnimeworksItem

class AnimeworksSpider(scrapy.Spider):
    name = "animeworks"
    allowed_domains = ["animeworks.com.au"]
    start_urls = ["https://animeworks.com.au/collections/pre-orders"]

    def parse(self, response):
        # Regex pattern to extract date only in [DD/MM/YYYY, D/MM/YYYY, DD/M/YYYY, D/M/YYYY] format
        date_pattern = r"\d{1,2}/\d{1,2}/\d{4}"
        # Scrapes product names, prices, release dates and images
        names = response.css("a.full-unstyled-link::text").getall()
        prices = response.css("span.price-item--regular::text").getall()
        release_dates = []
        for release in response.css("div.card-information"):
            release_date_text = release.css("h4::text").get()
            if release_date_text:
                match = re.search(date_pattern, release_date_text)
                if match:
                    release_dates.append(match.group())
                else:
                    release_dates.append(None)
            else:
                release_dates.append(None)
        images = [self._modify_image_url(source) for source in response.css("div.media > img::attr(src)").getall()]
        urls = ["https://animeworks.com.au" + source for source in response.css("div.card__information > h3 > a::attr(href)").getall()]

        # Create a new item for each product
        for i, _ in enumerate(names):
            item = AnimeworksItem()
            # Name (required)
            item["name"] = names[i].strip()
            # Price (required)
            item["price"] = prices[i].strip()
            # Release date (optional, may be None)
            item["release_date"] = release_dates[i]
            # Image (required)
            item["image"] = images[i]
            # URL (required)
            item["url"] = urls[i]
            # Send item
            yield item

        # Pagination
        next_page = response.css('a.pagination__item-arrow[aria-label="Next page"]::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    # Function to format image URLs correctly
    def _modify_image_url(self, url):
        # Remove query params
        url = re.sub(r'\?.*$', '', url)
        # Remove first two characters
        return re.sub(r"^.{2}", "", url)
