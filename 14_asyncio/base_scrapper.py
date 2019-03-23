import logging
from urllib.parse import urlparse

import config
import base_logic
logging.basicConfig(format=config.LOGGING_FORMAT,
                    datefmt=config.LOGGING_DATE_FORMAT, level=logging.INFO)


links = []

if __name__ == '__main__':
    base_page = base_logic.get_page_content(config.BASE_URL)
    soup = base_logic.beautiful_soup_instance(base_page)

    tr_items = base_logic.get_list_of_news(soup)
    for item in tr_items:
        id = item['id']
        news_title = item.find_all('td', {'class': 'title'})[-1].find('a').text
        detail_page = base_logic.get_page_content(
            config.DETAIL_PAGE.format(id)
        )
        base_logic.write_content_to_file(
            base_logic.file_name(news_title), detail_page
        )
        detail_page_parser = base_logic.beautiful_soup_instance(detail_page)
        detail_page_links = base_logic.get_all_nested_links(detail_page_parser)
        for link in detail_page_links:
            parsed_uri = urlparse(link)
            link_file_name = id + "_" + base_logic.file_name(
                parsed_uri.netloc.replace('.', '_')
            )
            link_page = base_logic.get_page_content(link)
            base_logic.write_content_to_file(link_file_name, link_page)
