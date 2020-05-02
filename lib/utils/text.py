import re

from funcy import compact, joining, partial

NORM = str.maketrans(
    {
        'e': 'е',
        'y': 'у',
        'o': 'о',
        'p': 'р',
        'a': 'а',
        'h': 'н',
        'k': 'к',
        'x': 'х',
        'c': 'с',
        'b': 'в',
        'm': 'м',
        'ё': 'е',
    }
)

RE_MISTYPES = re.compile(r'\b()\b', re.I)
RE_SPLIT = re.compile(r'[^\w\+-]+', re.U).split
RE_CYRILLIC = re.compile(r'[а-яё]').findall


@joining(' ')
def normalize(string: str):
    words = compact(RE_SPLIT(string.lower()))
    for word in words:
        if RE_CYRILLIC(word):
            yield word.translate(NORM)
        else:
            yield word


def format_int(src: int) -> str:
    return '{:,}'.format(src).replace(',', ' ')


RE_PRICE = partial(re.compile(r'\D+').sub, '')
CURRENCIES = {
    '₽': re.compile(r'(₽|руб)'),
    '€': re.compile(r'(€|евро)'),
    '$': re.compile(r'($|дол)'),
}


def format_price(src: str):
    price = RE_PRICE(src)
    if not price:
        # nothing found
        return src

    digits = format_int(int(price))
    for key, value in CURRENCIES.items():
        if value.search(src):
            return f'{digits} {key}'
    return src
