import requests
from bs4 import BeautifulSoup
import lxml
import re
from csv import writer

# Number of pages on jobs.ge
pageCount = len(BeautifulSoup(requests.get(
    'http://jobs.ge').content, 'lxml').find_all('a', {'class': 'pagebox'})) + 1


# A list to store all advertisment hrefs on jobs.ge
href_list = list()


# Iterate over each page on jobs.ge
for page in range(1, pageCount + 1):
    html = requests.get(
        f'http://jobs.ge/?page={page}&keyword=&cat=&location=&view=').content

    # Get all job entries
    jobs = BeautifulSoup(html, 'lxml').find(
        'div', {'class': 'regularEntries'}).find_all('tr')

    # Iterate over all jobs
    for job in jobs:
        try:
            """
            1. Find <a> tag that links to an advertisment
            2. Extract href
            3. Add the extracted href to the list of all hrefs
            """
            href_list.append(job.find(
                'a', {'class': 'ls'}, href=re.compile('\/[0-9]+\/')).attrs['href'])

            print('href added to the list')
        except AttributeError:
            # Skip the iteration if AttributeError occurs
            continue


# Dictionay for a single ad
advertisment = dict()


def openAd(href):
    """
    Access advertisment link and scrap the content
    1. Open advertisment
    2. Get all <tr> that containt advertisment information
    3. Construct and return Advertisment Dictionary
    """

    global advertisment

    # List to store needed <b> tags
    ad_list = list()

    html = requests.get('http://jobs.ge' + href).content

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
    advertisment['relative_url'] = href
    advertisment['absolute_url'] = 'http://jobs.ge' + href
    advertisment['translation_url'] = 'http://jobs.ge/eng' + href

    return advertisment


# Write CSV file from scrapped data
with open('advertisments.csv', 'w', encoding="utf-8") as csv_file:
    csv_writer = writer(csv_file)
    headers = ['title',
               'post_date',
               'final_date',
               'company',
               'lang',
               'translation',
               'ad_text',
               'absolute_url',
               'relative_url']
    csv_writer.writerow(headers)

    for href in href_list:
        openAd(href)
        csv_writer.writerow([advertisment['title'],
                             advertisment['post_date'],
                             advertisment['final_date'],
                             advertisment['company'],
                             advertisment['lang'],
                             advertisment['translation_url'],
                             advertisment['text'],
                             advertisment['absolute_url'],
                             advertisment['relative_url']])
        print('added to csv file')
