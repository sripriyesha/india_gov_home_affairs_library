# http://library.bjp.org/jspui/browse?type=title&sort_by=1&order=ASC&rpp=100&etal=0&submit_browse=Update

import scrapy


class BooksListSpider(scrapy.Spider):
    name = "books_list"
    start_urls = [
        # - Sorting by title (1)
        # - in order Ascending (ASC)
        # - Results/Page 100 (rpp)
        # - Authors/Record: All
        # - Offset 0 (first page)
        # - rpp = Results Per Page = 2642 (to get all books at once)
        # - etal = Et al. = "et alia" = "and others" = authors + contributors in this website
        'http://lsi.gov.in:8081/jspui/handle/123456789/1/browse?type=title&sort_by=1&order=ASC&rpp=7073&etal=0&submit_browse=Update'
    ]

    def parse(self, response):
        filename = 'books-list.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
