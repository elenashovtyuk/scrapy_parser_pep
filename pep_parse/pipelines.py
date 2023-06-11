# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import csv
import datetime as dt
# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from collections import defaultdict

# из файла settings.py импортируем константы
from pep_parse.settings import BASE_DIR, RESULT_DIR


class PepParsePipeline:
    # в методе __init__(self) мы задаем адрес расположения будущего файла
    def __init__(self):
        # cформируем путь до новой директории results
        # в BASE_DIR - у нас будет корневая папка
        # BASE_DIR = Path('SCRAPY_PARSER_PEP/results').parent.parent - вернет корневую папку
        # а RESULT_DIR вернет PosixPath('results')
        # итогом будет абсолютный путь до новой директории results
        self.filepath = BASE_DIR / RESULT_DIR
        # создаем директорию с помощью метода mkdir
        # укажем параметр exist_ok=True,
        # чтобы при повторном создании такой директории не возникала ошибка
        self.filepath.mkdir(exist_ok=True)

    # в модуле collections есть специальный тип для создания контейнера
    # defaultdict() - словарь с дефолтным значением для любого нового ключа
    # этот метод вызывается автоматически при запуске паука.
    # здесь мы можем выполнить некоторые операции инициализации
    # в данном случае мы создаем словарь defaultdict,
    # для каждого ключа(статуса) значение по умолчанию = 0
    # как только статус встречается,
    # то к кол-ву доков с этим статусов плюсуется 1
    def open_spider(self, spider):
        self.status_sum = defaultdict(int)

    # в этом методе происходит обработка каждого объекта Items
    # то есть, каждой страницы с документами, которые получены
    # от паука
    # item - каждый полученный (спарсенный)объект от паука
    # в нашем случае это каждая страница с документом PEP
    # spider - это паук, который парсил, собирал нужную инф-цию
    # в итоге метод должен вернуть либо обработанный item,
    # либо исключение
    # т.е. для каждого документа PEP мы проверяем наличие статуса
    # если статус уже встречался, то к уже имеющемуся кол-ву документов PEP
    # с этим статусом прибавится еще 1
    def process_item(self, item, spider):
        self.status_sum[item['status']] += 1
        return item

    # этот метод срабатывает при окончании работы паука
    def close_spider(self, spider):
        # в переменной dt_obj сохраним формат текущей даты и времмени
        # dt.datetime.utcnow() - абсолютное значение datetime
        # strftime() - метод,
        # с помощью которого конвертируем объект datetime в строку
        # и дальше используем его в названии файла
        dt_obj = dt.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        # сначала определим имя и тип будущего файла
        # формат задания по примеру в ТЗ
        filename = f'status_summary_{dt_obj}.csv'

        # далее нам нужно записать данные в файл
        # для этого с помощью контекстного менеджера вызовем open()
        # и передадим в него 2 аргумента:
        # 1-ый аргумент - абсолютное значение пути к открываемому файлу,
        # 2-ой аргумент - "w" - означает,
        # что файл нужно открыть в режиме записи
        with open(
            self.filepath / filename,
            mode='w',
            encoding='utf-8'
        ) as csvfile:
            # дальше с помощью функции write() cоздадим объект для записи
            csv_writer_file = csv.writer(
                # первый параметр - файловый объект
                csvfile,
                # второй параметр - dialect
                # cтрока с встроенным диалектом из списка csv.list_dialects()
                dialect=csv.unix_dialect,
                # третий параметр - quoting
                # указыввает, что ни одна запись не должна заключаться в кавычки
                # есть несколько вариантов
                # (ставить кавычки вокург всех значений, вокруг только нечисловых и тд)
                quoting=csv.QUOTE_NONE
            )
            # дальше нужно применить функцию writerows,
            # чтобы перебрать данные по строкам
            # в метод writerow() нужно передать список, котррый впоследствии
            # будет записан в файл через разделитель

            # 1-ая строка - Заголовки (Статус и Количество)
            csv_writer_file.writerows([
                ['Статус', 'Количество'],
                *self.status_sum.items(),
                ['Total', sum(self.status_sum.values())]
            ])
            # после выполнения этих действий в csv файл
            # будут сохранены нужные данные
