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


start = time.time()

"""
Collect All URLs
"""
entry_point = config.config['url']

try:
    xml = requests.get(entry_point, timeout=3).content
except ConnectionError:
    raise ConnectionError

raw_urls = BeautifulSoup(xml, 'lxml').find_all('guid')


# Collect all advertisment URLs in urls list
urls = []
for raw_url in raw_urls:
    urls.append(raw_url.text)
print('All links collected.')


"""
Collect category URLs
"""
categories = ['admin', 'sales', 'finance', 'prmarketing',
              'technical', 'it', 'law', 'healthcare', 'other']


category_list = {
    'admin': [],
    'sales': [],
    'finance': [],
    'prmarketing': [],
    'technical': [],
    'it': [],
    'law': [],
    'healthcare': [],
    'other': []
}


for category in categories:

    try:
        html = requests.get(
            f'http://jobs.ge/?page=1&keyword=&cat={category}&location=&view=', timeout=3).content
    except ConnectionError:
        raise ConnectionError

    bs = BeautifulSoup(html, 'lxml')

    page_count = get_page_count(bs)

    links = list()

    if page_count > 1:
        for page in range(1, page_count + 1):
            html = requests.get(
                f'http://jobs.ge/?page={page}&keyword=&cat={category}&location=&view=').content
            bs = BeautifulSoup(html, 'lxml')
            links += bs.find_all('a', {'class': 'ls'},
                                 href=re.compile(r'\/[0-9]+\/'))
    else:
        links += bs.find_all('a', {'class': 'ls'},
                             href=re.compile(r'\/[0-9]+\/'))

    for link in links:
        category_list[category].append(link.attrs['href'])


"""
Collect advertisment types URLs
"""
advertisment_types = ['jobs', 'scholarships', 'trainings', 'tenders', 'other']

advertisment_type_list = {
    'jobs': [],
    'scholarships': [],
    'trainings': [],
    'tenders': [],
    'other': []
}

for advertisment_type in advertisment_types:

    html = requests.get(
        f'http://jobs.ge/?page=1&keyword=&cat=&location=&view={advertisment_type}').content
    bs = BeautifulSoup(html, 'lxml')

    page_count = get_page_count(bs)

    links = list()

    if page_count > 1:
        for page in range(1, page_count + 1):
            html = requests.get(
                f'http://jobs.ge/?page={page}&keyword=&cat=&location=&view={advertisment_type}').content
            bs = BeautifulSoup(html, 'lxml')
            links += bs.find_all('a', {'class': 'ls'},
                                 href=re.compile(r'\/[0-9]+\/'))
    else:
        links += bs.find_all('a', {'class': 'ls'},
                             href=re.compile(r'\/[0-9]+\/'))

    for link in links:
        advertisment_type_list[advertisment_type].append(link.attrs['href'])


# Write CSV file from scrapped data
with open('advertisments.csv', 'w', encoding="utf-8") as csv_file:
    csv_writer = writer(csv_file)
    headers = ['სათაური',
               'განცხადების ტიპი',
               'გამოქვეყნების თარიღი',
               'საბოლოო თარიღი',
               'კატეგორია',
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
                             advertisment['company'],
                             advertisment['lang'],
                             advertisment['translation_url'],
                             advertisment['text'],
                             advertisment['absolute_url'],
                             advertisment['relative_url']
                             ])

end = time.time()

print((end - start) // 60)
