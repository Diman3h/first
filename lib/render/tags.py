import operator
import re
from dataclasses import asdict, dataclass, field
from functools import partial, reduce
from itertools import count
from typing import Dict

from funcy import post_processing

from ..config import (
    CITYESCAPE,
    LEVELS,
    NAPRAVLENIE,
    ORANGEKED,
    PIK,
    SHORT_DURATION,
    ZOVGOR,
)

bits = partial(next, count(1))


@dataclass
class Tag:
    for_json = asdict
    slug: str
    text: str
    title: str = ''
    bit: int = field(default_factory=lambda: 1 << bits())
    active: bool = True

    def __int__(self):
        return self.bit


class TagGroup:
    tags: Dict[str, Tag]

    def __init__(self, *tags: Tag):
        self.tags = {t.slug: t for t in tags}

    def __getitem__(self, item: str):
        return self.tags[item]

    def __iter__(self):
        return iter(self.tags.values())

    def for_json(self):
        tags = self.tags.values()
        return {
            'tags': tags,
            'bits': reduce_bits(tags),
        }


KIDS = Tag(slug='kids', title='с детьми', text='👶')
SHORT = Tag(slug='short', text='пвд')
LONG = Tag(slug='long', text='долгие')

VENDORS = TagGroup(
    Tag(slug=PIK, text='пик'),
    Tag(slug=ORANGEKED, text='оранжевый кед'),
    Tag(slug=CITYESCAPE, text='клуб походов и приключений'),
    Tag(slug=ZOVGOR, text='зов гор'),
    Tag(slug=NAPRAVLENIE, text='направление'),
)

LEVELS_TAGS = TagGroup(
    Tag(slug='level_1', text='очень просто'),
    Tag(slug='level_2', text='просто'),
    Tag(slug='level_3', text='средней сложности'),
    Tag(slug='level_4', text='сложно'),
    Tag(slug='level_5', text='очень сложно'),
)

MONTHS_NAMES = 'янв фев мар апр май июн июл авг сен окт ноя дек'.split()
MONTHS = TagGroup(
    *(Tag(slug=f'month_{m}', text=MONTHS_NAMES[m - 1]) for m in range(1, 13))
)

TAGS = (
    VENDORS,
    LEVELS_TAGS,
    TagGroup(SHORT, LONG),
    TagGroup(KIDS),
    MONTHS,
)


def reduce_bits(tags):
    return reduce(operator.or_, map(int, tags))


@post_processing(reduce_bits)
def get_tags(src: dict):
    yield VENDORS[src['vendor']]

    for bit, tag in zip(LEVELS, LEVELS_TAGS):
        if bit & src['level']:
            yield tag

    # fixme: kids tag duck style
    if re.findall(r'(семей|\([0-9]+\+\))', src['title'], re.I):
        yield KIDS

    # duration
    if (src['end'] - src['start']) <= SHORT_DURATION:
        yield SHORT
    else:
        yield LONG

    months = 1
    for m, month in enumerate(MONTHS, 1):
        in_month = (
            src['start'].month == m
            or src['end'].month == m
            or src['start'].month <= m <= src['end'].month
        )
        if in_month:
            months |= month.bit
    yield months
