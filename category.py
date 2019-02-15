# category.py

import re

import requests
from bs4 import BeautifulSoup
import lxml

from functions import get_page_count


def collect_category_links():
    """
    Collect Category URLs
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

    return category_list
