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


# Itterate over each page on jobs.ge
for page in range(1, pageCount + 1):
    html = requests.get(
        f'http://jobs.ge/?page={page}&keyword=&cat=&location=&view=').content
    bs = BeautifulSoup(html, 'lxml')

    # Get wrapper container for the regular ads
    ads_wrapper = bs.find('div', {'class': 'regularEntries'})

    # Get all trs
    all_trs = ads_wrapper.find_all('tr')

    # Itterate over all table rows
    for tr in all_trs:
        try:
            # Extract Advertisment <a> tags from table rows
            advertisment_link_tag = tr.find(
                'a', {'class': 'ls'}, href=re.compile('\/[0-9]+\/'))
            # Extract href addtibute from <a> tags
            advertisment_link_href = advertisment_link_tag.attrs['href']
            # Add extracted href to a list
            href_list.append(advertisment_link_href)
            print(f'{advertisment_link_href} added to the list')
        except AttributeError:
            # Skip the iteration if AttributeError occurs
            continue


# Dictionay for a single ad
advertisment = dict()


def openAd(href):
    """
    Access advertisment link and scrap the content
    """
    global advertisment
    ad_html = requests.get('http://jobs.ge' + href).content
    bs = BeautifulSoup(ad_html, 'lxml')

    # Get wrapper table of the advertisment
    ad_table = bs.find('table', {'class': 'ad'})

    # Return tr list
    ad_trs = ad_table.find_all('tr')

    # Get advertisment text from returned table rows
    ad_text = ad_trs.pop().text
    # Strip \n\r\t from advertisment text
    ad_text = re.sub(r'[\t\r\n]', '', ad_text)

    # List to store needed b tags
    ad_list = list()

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
    advertisment['relative_link'] = href
    advertisment['link'] = 'http://jobs.ge' + href
    advertisment['translation'] = 'http://jobs.ge/eng' + href

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
               'link',
               'relative_link']
    csv_writer.writerow(headers)

    for href in href_list:
        openAd(href)
        csv_writer.writerow([advertisment['title'],
                             advertisment['post_date'],
                             advertisment['final_date'],
                             advertisment['company'],
                             advertisment['lang'],
                             advertisment['translation'],
                             advertisment['text'],
                             advertisment['link'],
                             advertisment['relative_link']])
        print('added to csv file')
