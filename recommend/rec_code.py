from collections import OrderedDict
from difflib import SequenceMatcher
from typing import List, Iterable, Tuple, Generator, Iterator

import numpy as np
# from scipy.stats.stats import pearsonr

from .models import Place, Submission


# todo scikit cosine similarity


class Review:
    def __init__(self, reviewer, place, score):
        self.reviewer = reviewer # for now, a unique integer
        self.place = place  # models.Place
        # score can be
        self.score = score  # Always 1?

    def __repr__(self):
        return "Reviewer: {}  place: {}  score: {}".format(
            self.reviewer, self.place.city, self.score)


def find_reviews() -> np.ndarray:
    """Create a data set of all submissions."""
    reviews_ = []
    for i, submission in enumerate(Submission.objects.all()):
        for place in submission.places.all():
            reviews_.append(Review(i, place, 1))
    reviews = [(r.reviewer, r.place.id, r.score) for r in reviews_]

    return np.array(reviews)


def fake_data(place_1: Place, place_2: Place, data: np.ndarray):
    # Code to try to set 0 as a score for all reviewers who didn't
    # review that book.
    reviewers = np.unique(data[:, 0])

    for place in (place_1, place_2):

        reviews = data[data[:, 1] == place.id]

        # Reviewers who didn't review it.
        didnt_review = np.setdiff1d(reviewers, reviews[:, 0])
        n = didnt_review.size

        addition = np.column_stack([didnt_review, np.repeat(place.id, n), np.zeros(n)])
        data = np.vstack([data, addition])

    return data


def correlate(place_1: Place, place_2: Place, data: np.ndarray):
    # todo got to speed this up.
    """Calculate the pearson correlation coefficient between two places. Uses
    array instead of dataframes for speed."""
    data = fake_data(place_1, place_2, data)

    p1r = data[data[:, 1] == place_1.id]
    p2r = data[data[:, 1] == place_2.id]

    # Messy way of sorting an array; must line up the two by teh reviewer column.
    place_1_reviews = p1r[p1r[:, 0].argsort()]
    place_2_reviews = p2r[p2r[:, 0].argsort()]

    # todo we could use scipy.stats.pearsonr, np.corrcoef, or brisk.corr
    # correlation_coefficient = pearsonr(place_1_reviews[:, 2], place_2_reviews[:, 2])[0]
    correlation_coefficient = np.corrcoef(place_1_reviews[:, 2], place_2_reviews[:, 2])[0, 1]

    # import brisk
    # correlation_coefficient = brisk.corr(place_1_reviews.score, place_2_reviews.score)

    # We know how they related
    return correlation_coefficient


def find_similar(place: Place) -> OrderedDict:
    """"""
    data = find_reviews()

    # Ignore this place if there are no existing submissions for it.
    if place.id not in data[:, 1]:
        return {}

    # todo use a filter for low, instead of no, review places.
    # Ignore places that have no reviewers.
    query = Place.objects.filter(id__in=data[:, 1])
    scores = {place2: correlate(place, place2, data) for place2 in query}

    return OrderedDict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def find_similar_multiple(similars: Iterable[OrderedDict]):
    """Organizes data from individual similarity rankings for each place."""
    composite_scores = {}
    for similar in similars:
        for city, score in similar.items():
            try:
                composite_scores[city].append(score)
            except KeyError:
                composite_scores[city] = [score]

    result = {}
    for city, scores in composite_scores.items():
        # todo find a better function than mean
        import numpy as np
        result[city] = np.mean(scores)

    return OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse=True))


def find_db_entries(places: Iterable[str]) -> Iterator[Place]:
    """Accept place name strings, as passed from a web form; find their
    corresponding database entries."""
    min_match_ratio = .8

    # todo if matches are identical or similar (florence italy vs usa), use
    # todo number of submissions to pick the most popular.

    for place_name in places:
        ratios = []
        # Narrow the number of objects to filter with a startswith query.
        for place in Place.objects.filter(city__istartswith=place_name[:2]):
            ratios.append((place, SequenceMatcher(None, place_name, place.city).quick_ratio()))

        filtered = filter(lambda x: x[1] > min_match_ratio, ratios)
        matches = sorted(filtered, key=lambda x: x[1], reverse=True)

        if not matches:
            continue

        # Find matches tied for the lead.
        tops = [matches[0]]
        for match in matches[1:]:
            if match[1] == tops[0][1]:
                tops.append(match)

        # Find the most popular match of those tied for the lead.
        reviews = find_reviews()
        counts = []
        for place in (place_[0] for place_ in tops):
            counts.append((place, (reviews[:, 1] == place.id).sum()))
        most_popular = max(counts, key=lambda x: x[1])
        yield most_popular[0]

        # todo return only the top result for now.
        # yield matches[0][0]


def process_input(place_str: str):
    """Find recommendations based on input places."""
    places = (place.strip() for place in place_str.split(','))

    entries = find_db_entries(places)
    entries = list(entries)
    print("DB entries:", entries)

    similars = (find_similar(place) for place in entries)

    return find_similar_multiple(similars)

