import re

import requests
from bs4 import BeautifulSoup
import lxml

from functions import get_page_count
from functions import get_html


def collect_category_links() -> list:
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

        bs = BeautifulSoup(get_html(
            f'http://jobs.ge/?page=1&keyword=&cat={category}&location=&view='), 'lxml')

        page_count = get_page_count(bs)

        links = list()

        if page_count > 1:
            for page in range(1, page_count + 1):

                bs = BeautifulSoup(get_html(
                    f'http://jobs.ge/?page={page}&keyword=&cat={category}&location=&view='), 'lxml')

                links += bs.find_all('a', {'class': 'ls'},
                                     href=re.compile(r'\/[0-9]+\/'))
        else:
            links += bs.find_all('a', {'class': 'ls'},
                                 href=re.compile(r'\/[0-9]+\/'))

        for link in links:
            category_list[category].append(link.attrs['href'])

    return category_list
