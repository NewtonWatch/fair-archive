import os
import csv
import datetime
import requests
from bs4 import BeautifulSoup


def to_file(content, filename, extension):
    path, filename = filename.rsplit('/', 1)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f'{path}/{filename}.{extension}', 'w') as file:
        file.write(content)


def list_to_csv(content, filename):
    with open(f'{filename}.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(zip(content))


def get_page_content(url):
    return requests.get(url).content


def remove_non_fair_urls(urls):
    keep_urls = []
    for url in urls:
        if url.startswith('https://fair.org/home/'):
            keep_urls.append(url)
    keep_urls = list(set(keep_urls))
    keep_urls.sort()
    return keep_urls


def get_page_fair_urls(url):
    page = get_page_content(url)
    soup = BeautifulSoup(page, 'html.parser')
    results = soup.find_all('a', href=True)
    urls = []
    for url in results:
        urls.append(url.get('href'))
    return urls


# Note: this is slow. Only run once if you can.
def get_all_fair_urls():
    fair_urls = []
    max_pages = 491
    for page_number in range(1, max_pages + 1):
        base_url = f'https://fair.org/page/{page_number}'
        print(base_url)
        page_urls_found = get_page_fair_urls(base_url)
        fair_urls_found = remove_non_fair_urls(page_urls_found)
        fair_urls.extend(fair_urls_found)
        list_to_csv(fair_urls_found, f'csv/page_{page_number}')
        list_to_csv(fair_urls, 'csv/all_fair_urls')


def get_urls_from_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return list(set([item for sublist in data for item in sublist]))


def get_page_meta_and_html(url):
    page = get_page_content(url)
    soup = BeautifulSoup(page, 'html.parser')
    # TODO: Replace all non-alpha non-numeric characters. 
    page_title = soup.title.string.replace(' — FAIR', '').replace('/', '_').replace(' ', '_').replace("'", '_')
    page_date = soup.select('.fair_list_date')[0].string
    page_author = soup.select('.fair_list_author')[0].find_all('a', href=True)[0].string.replace(' ', '_')
    page_html = soup.prettify()
    page_date = datetime.datetime.strptime(page_date, '%B %d, %Y').strftime('%Y_%B_%d')
    return page_title, page_date, page_author, page_html


if __name__ == '__main__':
    # get_all_fair_urls()

    processed_urls = []
    all_urls = get_urls_from_csv('csv/all_fair_urls.csv')
    url = all_urls[0]

    for url in all_urls:
        page_title, page_date, page_author, page_html = get_page_meta_and_html(url)
        page_year = page_date[0:4]
        to_file(page_html, f'articles/html/{page_year}/{page_title}_{page_author}', 'html')
        processed_urls.append(url)
        print(f'{len(processed_urls)} out of {len(all_urls)}')
        list_to_csv(processed_urls, 'csv/processed_urls')
