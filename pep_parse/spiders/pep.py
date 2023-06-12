import scrapy
from pep_parse.items import PepParseItem


class PepSpider(scrapy.Spider):
    name = 'pep'
    allowed_domains = ['peps.python.org']
    start_urls = ['https://peps.python.org/', ]

    def parse(self, response):
        """Собирает ссылки на все документы PEP."""
        all_docs = response.css('#numerical-index td a::attr(href)').getall()
        for doc_link in all_docs:
            yield response.follow(doc_link, callback=self.parse_pep)

    def parse_pep(self, response):
        """
        Парсит страницы документов PEP по полученным ссылкам и формирует Items.
        """
        number, name = response.css('h1.page-title::text').get().split(' – ')
        data = {
            'number': number.replace('PEP ', ''),
            'name': name,
            'status': response.css(
                'dt:contains("Status") + dd abbr::text').get(),
        }
        yield PepParseItem(data)
