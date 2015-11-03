"""This file provides an API interface to google books."""

from collections import namedtuple
import datetime as dt
from difflib import SequenceMatcher

import requests
from typing import Tuple

from books.auth import goog_key as key


Book = namedtuple('Book', ['title', 'authors', 'isbn_10', 'isbn_13', 'publication_date'])

base_url = 'https://www.googleapis.com/books/v1/'


def search_title(title):
    url = base_url + 'volumes'
    payload = {'q': 'intitle:"{}"'.format(title),
               'printType': 'books',
               'projection': 'full'}

    result = requests.get(url, params=payload)

    result = result.json()
    result = [book['volumeInfo'] for book in result['items']]

    return _trim_results(result)


def search_author(author):
    url = base_url + 'volumes'
    payload = {'q': 'inauthor:"{}"'.format(author),
               'printType': 'books'}

    result = requests.get(url, params=payload)

    result = result.json()
    result = [book['volumeInfo'] for book in result['items']]

    return _trim_results(result)


def search(title='', author=''):
    # The author/title composite match ratio must exceed this to be returned.
    min_match_ratio = .3

    url = base_url + 'volumes'
    payload = {'q': 'intitle:{}+inauthor:{}'.format(title, author),
               'printType': 'books'}

    result = requests.get(url, params=payload)

    result = result.json()
    result = [book['volumeInfo'] for book in result['items']]

    trimmed = _trim_results(result)

    ratios = []
    for book in trimmed:
        title_ratio = SequenceMatcher(None, title.lower(), book.title.lower()).ratio()

        author_ratios = [SequenceMatcher(None, author.lower(), author_goog.lower()).ratio() for
                         author_goog in book.authors]
        # We're only searching for one author, so find the best match in the
        # authors list google returns, and ignore the rest.
        best_author_ratio = max(author_ratios)
        composite = composite_ratio(title_ratio, best_author_ratio)
        ratios.append((book, title_ratio, best_author_ratio, composite))

    sequenced = sorted(ratios, key=lambda x: x[3], reverse=True)

    filtered = filter(lambda x: x[3] > min_match_ratio, sequenced)

    return list(filtered)


def composite_ratio(ratio_1: float, ratio_2: float) -> float:
    try:
        return 1 / (1/ratio_1 + 1/ratio_2)
    except ZeroDivisionError:
        return 0


def _trim_results(raw_data):
    """Reformat raw Google Books api data into a format with only information
    we care about."""
    result = []
    for book in raw_data:
        try:
            pub_date = dt.datetime.strptime(book['publishedDate'],
                                            '%Y-%m-%d').date()
        except ValueError:
            pub_date = book['publishedDate']
        except KeyError:
            pub_date = 'missing'

        isbn_10 = ''
        isbn_13 = ''
        try:
            isbn_raw = book['industryIdentifiers']

            for num in isbn_raw:
                if num['type'] == 'ISBN_13':
                    isbn_13 = num['identifier']
                elif num['type'] == 'ISBN_10':
                    isbn_10 = num['identifier']

        # This keyerror means 'industryIdentifiers' is missing entirely; if
        # it's present, but doens't have 'isbn_13/10' subkeys, it doesn't
        # come up.
        except KeyError:
            pass
        result.append(
            Book(book['title'], book['authors'], isbn_10, isbn_13, pub_date)
        )
    return result
