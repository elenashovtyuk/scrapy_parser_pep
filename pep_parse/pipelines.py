import csv
import datetime as dt
from collections import defaultdict

from pep_parse.settings import BASE_DIR, RESULT_DIR


class PepParsePipeline:

    def __init__(self):
        """
        Задаем адрес расположения будущего файла со сводкой
        по статусам PEP-документов.
        """
        self.filepath = BASE_DIR / RESULT_DIR
        self.filepath.mkdir(exist_ok=True)

    def open_spider(self, spider):
        """
        Подготовка к записи спарсенных данных.
        """
        self.status_sum = defaultdict(int)

    def process_item(self, item, spider):
        """
        Обработка данных, по одному полученному элементу за раз.
        """
        self.status_sum[item['status']] += 1
        return item

    def close_spider(self, spider):
        """
        Завершаем экспорт данных в csv-файл.
        """
        dt_obj = dt.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'status_summary_{dt_obj}.csv'

        with open(
            self.filepath / filename,
            mode='w',
            encoding='utf-8'
        ) as csvfile:
            csv_writer_file = csv.writer(
                csvfile,
                dialect=csv.unix_dialect,
                quoting=csv.QUOTE_NONE
            )

            csv_writer_file.writerows([
                ['Статус', 'Количество'],
                *self.status_sum.items(),
                ['Total', sum(self.status_sum.values())]
            ])
