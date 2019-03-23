import os
import re

import requests
from bs4 import BeautifulSoup

import config


def file_name(full_name):
    """Process filename."""
    return str(full_name).lower().replace(' ', '_') + ".html"


def get_page_content(url, timeout=config.DEFAULT_TIMEOUT):
    """Return html page for the given url."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.content
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return get_page_content(url, timeout + 3)


def write_content_to_file(filename, content):
    """Create file in current directory and write there page content."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.isfile(path):
        f = open(path, 'w+')
        try:
            encoded_content = content.decode('utf-8', errors="ignore")
        except:
            encoded_content = content
        f.write(encoded_content)
        f.close()


def beautiful_soup_instance(page):
    """Return instance of BeautifulSoup class."""
    return BeautifulSoup(page, 'html.parser')


def get_list_of_news(soup):
    """Return list of news items."""
    page_content = soup.select_one('table > tr:nth-of-type(3)')
    tr_items = page_content.select_one('table').find_all('tr', attrs={
        'id': True
    })
    return tr_items


def get_all_nested_links(soup):
    """Return all nested links for the detail page."""
    return soup.find_all(
        text=re.compile('http(s)://')
    )
