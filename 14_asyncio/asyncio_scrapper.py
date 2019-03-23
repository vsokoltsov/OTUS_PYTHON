#!/bin/python

import asyncio
import aiohttp
import async_timeout
from urllib.parse import urlparse
import logging

import config
import base_logic
from optparse import OptionParser
logging.basicConfig(format=config.LOGGING_FORMAT,
                    datefmt=config.LOGGING_DATE_FORMAT, level=logging.INFO)


async def request(url):
    """Implement async request and return page content."""
    page_content = None
    try:
        async with async_timeout.timeout(config.DEFAULT_TIMEOUT):
            async with aiohttp.ClientSession() as session:
                async with session.get(str(url)) as response:
                    page_content = await response.text()
    except asyncio.TimeoutError:
        logging.exception("EXCEPTION timeout error for {}".format(
            url
        ))
    except Exception as e:
        logging.exception("EXCEPTION unknown error for {}".format(
            url
        ))
    return page_content


async def sleep(timeout):
    """Timeout for asyncio."""
    await asyncio.sleep(timeout)


async def news(queue):
    """List of news on the ycombinator page."""
    page_content = await request(config.BASE_URL)
    if page_content:
        soup = base_logic.beautiful_soup_instance(page_content)
        tr_items = base_logic.get_list_of_news(soup)
        for item in tr_items:
            id = item['id']
            news_title = item.find_all(
                'td', {'class': 'title'}
            )[-1].find('a').text
            url = config.DETAIL_PAGE.format(id)
            queue.put_nowait({'id': id, 'title': news_title, 'url': url})


async def runner(queue, download_queue):
    """Run base scrapper loop."""
    while True:
        logging.info("ITERATION")
        asyncio.ensure_future(news(queue))
        queue.join()
        await sleep(60)


async def write_content(download_queue):
    """Listen queue and write queue element to file."""
    while True:
        while not download_queue.empty():
            file_data = download_queue.get_nowait()
            filename = file_data.get('filename')
            page = file_data.get('page')

            base_logic.write_content_to_file(filename, page)
        await sleep(1)


async def handle_link(queue, download_queue):
    """Handle every ycombinator news item."""
    while True:
        while not queue.empty():
            news_hash = queue.get_nowait()
            title = news_hash.get('title')
            url = news_hash.get('url')
            detail_page = await request(url)

            if detail_page:
                params = {
                    'filename': base_logic.file_name(title),
                    'page': detail_page
                }
                download_queue.put_nowait(params)
                detail_page_parser = base_logic.beautiful_soup_instance(
                    detail_page
                )
                detail_page_links = base_logic.get_all_nested_links(
                    detail_page_parser
                )
                await asyncio.ensure_future(
                    parse_detail_links(download_queue, detail_page_links))
                queue.task_done()

        await sleep(1)


async def parse_detail_links(download_queue, links):
    """Put into the queue all the links from the news page."""
    for link in links:
        link_page = await request(link)
        if link_page:
            parsed_uri = urlparse(link)
            link_file_name = base_logic.file_name(
                parsed_uri.netloc.replace('.', '_')
            )
            params = {
                'filename': link_file_name,
                'page': link_page
            }
            download_queue.put_nowait(params)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--parsers", action="store", type="int",
                  default=config.DEFAULT_PARSERS)
    op.add_option("-l", "--loaders", action="store", type="int",
                  default=config.DEFAULT_LOADERS)

    (opts, args) = op.parse_args()
    parser_queue = asyncio.Queue()
    download_queue = asyncio.Queue()

    ioloop = asyncio.get_event_loop()
    for _ in range(opts.parsers):
        ioloop.create_task(handle_link(parser_queue, download_queue))
    for _ in range(opts.loaders):
        ioloop.create_task(write_content(download_queue))
    ioloop.run_until_complete(runner(parser_queue, download_queue))
    ioloop.run_forever()
    ioloop.close()
