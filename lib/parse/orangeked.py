import re
from datetime import datetime
from typing import Iterator

from funcy import compose, first
from lxml import html

from ..config import TODAY, Level, Vendor
from ..models import Item
from ..utils import gather_chunks, silent
from . import client

MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)
parse_dates = compose(
    first, re.compile(r'([0-9]+) (\w*) ?- ([0-9]+) (\w+)').findall,
)


async def parse_orangeked() -> Iterator[Item]:
    listing = await client.get('http://orangeked.ru/tours')
    tree = html.fromstring(listing.text.encode())
    links = set(tree.xpath('//*[@id="tourList"]/div/div/div/a/@href'))
    return iter(await gather_chunks(5, *map(parse_page, links)))


@silent
async def parse_page(path: str) -> Item:
    url = 'http://orangeked.ru' + path
    page = await client.get(url)
    tree = html.fromstring(page.text.encode())
    level = len(tree.xpath('//*[@class="icons-difficulty"]/i[@class="i"]'))
    slots = len(tree.xpath('//*[@class="icons-groupsize"]/i[@class="i"]'))
    title = tree.xpath('//*[@id="k2Container"]/header/h1/text()')[0]
    start, end = parse_date(
        tree.xpath('//*[@class="tour__short-info__item__value"]/text()')[1]
    )
    price = tree.xpath('//*[@class="tour__short-info__item__value"]/text()')[
        2
    ]
    item = Item(
        vendor=Vendor.ORANGEKED,
        level=Level.index(level - 1),
        start=start,
        end=end,
        url=url,
        title=title,
        price=price,
        slots=slots,
    )
    return item


def parse_date(src: str):
    start_day, start_month, end_day, end_month = parse_dates(src)
    start_month = start_month or end_month
    start_month = MONTHS.index(start_month) + 1
    end_month = MONTHS.index(end_month) + 1

    start_year = end_year = TODAY.year

    if end_month < TODAY.month < start_month:
        end_year += 1

    yield datetime(start_year, start_month, int(start_day))
    yield datetime(end_year, end_month, int(end_day))
