# scrapper.py

import re
import time
from csv import writer

import requests
from bs4 import BeautifulSoup
import lxml

import config

from functions import open_ad
from functions import get_page_count
from functions import add_property
from functions import get_html

from category import collect_category_links
from type import collect_ad_type_links


start = time.time()

entry_point = config.config['url']
raw_urls = BeautifulSoup(get_html(entry_point), 'lxml').find_all('guid')


# Collect all advertisment URLs in urls list
urls = [raw_url.text for raw_url in raw_urls]
print('All links collected.')

category_list = collect_category_links()
print('Category list collected.')


advertisment_type_list = collect_ad_type_links()
print('Ad types list collected.')


# Write CSV file from scrapped data
with open('advertisments.csv', 'w', encoding="utf-8") as csv_file:
    csv_writer = writer(csv_file)
    headers = ['სათაური',
               'განცხადების ტიპი',
               'გამოქვეყნების თარიღი',
               'საბოლოო თარიღი',
               'კატეგორია',
               'ლოკაცია',
               'კომპანია',
               'განცხადების ენა',
               'თარგმანის ლინკი',
               'განცხადება',
               'Absolute URL',
               'Relative URL']
    csv_writer.writerow(headers)

    advertisment = dict()
    for url in urls:
        open_ad(advertisment, url)

        add_property(advertisment, category_list, 'category',
                     advertisment['absolute_url'])

        add_property(advertisment,
                     advertisment_type_list, 'type', advertisment['absolute_url'])

        csv_writer.writerow([advertisment['title'],
                             advertisment['type'],
                             advertisment['post_date'],
                             advertisment['final_date'],
                             advertisment['category'],
                             advertisment['location'],
                             advertisment['company'],
                             advertisment['lang'],
                             advertisment['translation_url'],
                             advertisment['text'],
                             advertisment['absolute_url'],
                             advertisment['relative_url']
                             ])

end = time.time()

print((end - start) // 60)
