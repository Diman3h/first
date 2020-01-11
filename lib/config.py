import os.path
from datetime import timedelta
from functools import partial

import click

info = partial(click.secho, color='white', bold=True)

abs_path = partial(os.path.join, os.path.dirname(os.path.realpath(__file__)))
src_path = partial(abs_path, '../src')
DIST_DATA = abs_path('../www/data.js')

ORANGEKED = 'orangeked'
PIK = 'pik'
CITYESCAPE = 'cityescape'
VENDORS = (ORANGEKED, PIK, CITYESCAPE)

DATE_FORMAT = '%d.%m.%Y'
SHORT_DURATION = timedelta(days=3)
WEEKENDS = [
    '01.01.2020',
    '02.01.2020',
    '03.01.2020',
    '06.01.2020',
    '07.01.2020',
    '08.01.2020',
    '03.01.2020',
    '24.02.2020',
    '09.03.2020',
    '01.05.2020',
    '04.05.2020',
    '05.05.2020',
    '11.05.2020',
    '12.06.2020',
    '04.11.2020',
]
