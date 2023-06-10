import scrapy
from pep_parse.items import PepParseItem


class PepSpider(scrapy.Spider):
    name = 'pep'
    allowed_domains = ['peps.python.org']
    start_urls = ['http://peps.python.org/']

    # имеем дело с обработкой страниц с разной структурой
    # метод parse() должен собирать ссылки на документы PEP
    def parse(self, response):
        # находим все ссылки на документы PEP
        all_docs = response.css('#numerical-index td a::attr(href)').getall()
        # перебираем в цикле ссылки на документы PEP
        # и для каждой ссылки на документ нам нужно осуществить:
        # переход по этой ссылке, т.е загрузку страницы для каждого документа
        # и вызов метода parse_pep для каждой из них
        # чтобы спарсить нужную информацию о каждом документе
        # Возвращаем response.follow() с вызовом метода parse_pep()
        for doc_link in all_docs:
            yield response.follow(doc_link, callback=self.parse_pep)

    # парсит страницы документов PEP по собранным ссылкам
    def parse_pep(self, response):
        # парсинг страницы документа PEP
        # сохранение спарсенных данных в словарь и
        # возврат полученных данных в виде Items

        # номер и название документа находятся в одной строке и разделены
        # символом "-"
        number, name = response.css('h1.page-title::text').get().split(' – ')
        data = {
            'number': number.replace('PEP ', ''),
            'name': name,
            'status': response.css(
                'dt:contains("Status") + dd abbr::text').get(),
        }
        # словарь с полученными данными передаем в конструктор класса
        # PepParseItem
        yield PepParseItem(data)
