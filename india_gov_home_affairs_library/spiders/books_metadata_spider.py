import os
import pathlib
import urllib.parse

import scrapy
from scrapy.http import Request


class BooksMetadataSpider(scrapy.Spider):
    name = "books_metadata"
    start_urls = [
        "http://lsi.gov.in:8081/jspui/handle/123456789/1/browse?type=title&sort_by=1&order=ASC&rpp=7073&etal=0&submit_browse=Update"
        # pathlib.Path(os.path.abspath('books-list.html')).as_uri()
    ]

    def parse(self, response):
        book_page_links = response.xpath("//td[@headers='t2']//@href")
        yield from response.follow_all(book_page_links, self.parse_book_page)

    def parse_book_page(self, response):
        def get_metadata():
            def extract_with_css(query):
                return response.css(query).get(default="").strip()

            return {
                # "ISSUEDT": extract_with_css(
                #     "td.metadataFieldValue.dc_date_issued::text"
                # ),
                "title": extract_with_css("td.metadataFieldValue::text"),
                "filetitle": response.xpath("//td[@headers='t1']//a//text()")
                .get(default="")
                .strip(),
                "titleurl": response.request.url,
                "author": extract_with_css(".author::text"),
                "authorurl": response.urljoin(extract_with_css(".author::attr(href)")),
                "description": response.xpath(
                    "//td[contains(text(), 'Description:')]"
                    + "/following-sibling::td[1 and @class='metadataFieldValue']"
                    + "//text()"
                )
                .get(default="")
                .strip(),
                "censusyear": response.xpath(
                    "//td[contains(text(), 'Census Year:')]"
                    + "/following-sibling::td[1 and @class='metadataFieldValue']"
                    + "//text()"
                )
                .get(default="")
                .strip(),
                "collection": response.xpath(
                    "//td[contains(text(), 'Appears in Collections:')]"
                    + "/following-sibling::td[1 and @class='metadataFieldValue']"
                    + "//a//text()"
                )
                .get(default="")
                .strip(),
                "collectionurl": response.urljoin(
                    response.xpath(
                        "//td[contains(text(), 'Appears in Collections:')]"
                        + "/following-sibling::td[1 and @class='metadataFieldValue']"
                        + "//@href"
                    )
                    .get(default="")
                    .strip()
                ),
            }

        file_relative_url = (
            response.xpath("//td[@headers='t1']//@href").get(default="").strip()
        )
        file_abs_url = response.urljoin(file_relative_url)

        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
            "Sec-Fetch-User": "?1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # yield Request(file_abs_url, callback=self.save_file, headers=headers)

        yield get_metadata()

    def save_file(self, response):
        path = "./books/" + urllib.parse.unquote(response.url.split("/")[-1])
        self.logger.info("Saving file %s", path)
        with open(path, "wb") as f:
            f.write(response.body)
