import re
from datetime import datetime

import httpx
from lxml import html

from lib.config import TEAMTRIP
from lib.models import Item
from lib.utils import error, zip_safe

MONTHS = (
    'января февраля марта апреля мая июня июля августа '
    'сентября октября ноября декабря'.split()
)


async def parse_teamtrip():
    page = await httpx.get('https://team-trip.ru/')
    return parse_page(page.text)


def parse_page(text):
    tree = html.fromstring(text.encode())
    paths = (
        '//*[@class="t404__tag"]/text()',
        '//*[@class="t404__title t-heading t-heading_xs"]/text()',
        '//*[@class="t404__link"]/@href',
    )
    now = datetime.now()
    for dates, title, url in zip_safe(*map(tree.xpath, paths)):
        for date in re.sub(r'\,\s+([0-9]{,2}[\s-])', r'/\1', dates).split(
            '/'
        ):
            try:
                start, end = parse_dates(now, date)
            except Exception as e:
                error(f'Failed to parse data "{dates}" ({e})')
                continue

            yield Item(
                vendor=TEAMTRIP,
                start=start,
                end=end,
                title=title,
                url='https://team-trip.ru' + url,
            )


def parse_dates(now: datetime, src: str):
    start_, end_ = map(str.strip, re.split(r'[–\-]', src))
    end = parse_date(now, end_)
    start = parse_date(end, start_)
    return start, end


def parse_date(now, source):
    # 31декабря
    fixed = re.sub(r'([0-9])([a-zа-я])', r'\1 \2', source)
    data = re.split(r'\W+', fixed)
    if len(data) == 3:
        day, month, year = data
        return datetime(
            day=int(day), month=MONTHS.index(month) + 1, year=int(year)
        )
    elif len(data) == 2:
        day, month = data
        return now.replace(day=int(day), month=MONTHS.index(month) + 1)
    else:
        return now.replace(day=int(data[0]))