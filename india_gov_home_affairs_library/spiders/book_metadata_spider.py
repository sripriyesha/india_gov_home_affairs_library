import os
import pathlib
import urllib.parse

import scrapy
from scrapy.http import Request


class BookMetadataSpider(scrapy.Spider):
    name = "book_metadata"
    start_urls = [
        # example book page
        "http://lsi.gov.in:8081/jspui/handle/123456789/106"
    ]

    def parse(self, response):
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
        # yield Request(file_abs_url, callback=self.save_file)

        yield get_metadata()

    def save_file(self, response):
        path = "./books/" + urllib.parse.unquote(response.url.split("/")[-1])
        self.logger.info("Saving file %s", path)
        with open(path, "wb") as f:
            f.write(response.body)
