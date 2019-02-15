# functions.py

import re

import requests
from bs4 import BeautifulSoup
import lxml


def add_property(ad: dict, itterable: list, property: str, url: str) -> str:
    """
    Add category or type to advertisment
    """
    for key, values in itterable.items():
        for value in values:
            if value == url[18:]:
                ad[property] = key


def open_ad(dictionary: dict, url: str) -> dict:
    """
    Access advertisment link and scrap the content
    1. Open advertisment
    2. Get all <tr> that containt advertisment information
    3. Construct and return Advertisment Dictionary
    """

    ad_list = list()

    html = requests.get(url).content

    # Get all <tr> inside <table class="ad">
    ad_trs = BeautifulSoup(html, 'lxml').find(
        'table', {'class': 'ad'}).find_all('tr')

    # Get advertisment text from returned table rows
    # Strip \n\r\t from advertisment text
    ad_text = re.sub(r'[\t\r\n]', '', ad_trs.pop().text)

    # Iterate over ad_trs and append <b> tags to ad_list list
    for tr in ad_trs:
        ad_properties = tr.find_all('b')
        ad_list.append(ad_properties)

    # Ad location is in title > i
    if ad_list[0][0].find('i'):
        location = ad_list[0][0].find('i').text.split(',')
    else:
        location = ['თბილისი']

    # assign properties to ad dictionary
    dictionary['title'] = ad_list[0][0].text
    dictionary['location'] = location
    dictionary['company'] = ad_list[1][0].text
    dictionary['post_date'] = ad_list[2][0].text
    dictionary['final_date'] = ad_list[2][1].text
    dictionary['text'] = ad_text
    dictionary['lang'] = 'ქართული'
    dictionary['relative_url'] = url[18:]
    dictionary['absolute_url'] = url
    dictionary['translation_url'] = 'http://jobs.ge/eng' + url[18:]

    return dictionary


def get_page_count(html: list) -> int:
    """
    Get page count
    """
    pages = len(html.find_all('a', {'class': 'pagebox'})) + 1
    return pages


def get_html(url: str):
    """
    Provide error checking for getting html with requests library
    """
    try:
        html = requests.get(url, timeout=3)

        if html.status_code != 200:
            raise ConnectionError

    except ConnectionError:
        print('Connection Error encountered!')
    else:
        html = html.text

    return html
