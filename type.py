# type.py

import re

import requests
from bs4 import BeautifulSoup
import lxml

from functions import get_page_count


def collect_ad_type_links():
    """
    Collect advertisment types URLs
    """
    advertisment_types = ['jobs', 'scholarships',
                          'trainings', 'tenders', 'other']

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
            advertisment_type_list[advertisment_type].append(
                link.attrs['href'])

    return advertisment_type_list
