import requests
from bs4 import BeautifulSoup
import lxml
import re
from csv import writer

'''
Collect All URLs
'''
xml = requests.get('http://www.jobs.ge/rss/').content

raw_urls = BeautifulSoup(xml, 'lxml').find_all('guid')

urls = []

for raw_url in raw_urls:
    urls.append(raw_url.text)


'''
Collect category URLs
'''
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

    html = requests.get(
        f'http://jobs.ge/?page=1&keyword=&cat={category}&location=&view=').content
    bs = BeautifulSoup(html, 'lxml')
    links = bs.find_all('a', {'class': 'ls'}, href=re.compile('\/[0-9]+\/'))

    for link in links:
        category_list[category].append(link.attrs['href'])

# Dictionay for a single ad
advertisment = dict()


def openAd(url):
    """
    Access advertisment link and scrap the content
    1. Open advertisment
    2. Get all <tr> that containt advertisment information
    3. Construct and return Advertisment Dictionary
    """

    global advertisment

    # List to store needed <b> tags
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

    # assign properties to ad dictionary
    advertisment['title'] = ad_list[0][0].text
    advertisment['company'] = ad_list[1][0].text
    advertisment['post_date'] = ad_list[2][0].text
    advertisment['final_date'] = ad_list[2][1].text
    advertisment['text'] = ad_text
    advertisment['lang'] = 'ქართული'
    advertisment['relative_url'] = url[18:]
    advertisment['absolute_url'] = url
    advertisment['translation_url'] = 'http://jobs.ge/eng' + url[18:]

    for key, values in category_list.items():
        for value in values:
            if value == url[18:]:
                advertisment['category'] = key

    return advertisment


# Write CSV file from scrapped data
with open('advertisments.csv', 'w', encoding="utf-8") as csv_file:
    csv_writer = writer(csv_file)
    headers = ['title',
               'post_date',
               'final_date',
               'category',
               'company',
               'lang',
               'translation',
               'ad_text',
               'absolute_url',
               'relative_url']
    csv_writer.writerow(headers)

    for url in urls:
        openAd(url)
        csv_writer.writerow([advertisment['title'],
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
        print('added to csv file')
