from collections import OrderedDict
from difflib import SequenceMatcher
from typing import List, Iterable, Tuple

import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr

from .models import Place, Submission


class Review:
    def __init__(self, reviewer, place, score):
        self.reviewer = reviewer # for now, a unique integer
        self.place = place  # models.Place
        # score can be
        self.score = score  # Always 1?

    def __repr__(self):
        return "Reviewer: {}  place: {}  score: {}".format(
            self.reviewer, self.place.city, self.score)



def find_reviews() -> pd.DataFrame:
    """Create a data set of all submissions."""
    reviews_ = []
    for i, submission in enumerate(Submission.objects.all()):
        for place in submission.places.all():
            reviews_.append(Review(i, place, 1))
    reviews = [(r.reviewer, r.place.id, r.score) for r in reviews_]

    data = pd.DataFrame(reviews, columns=['reviewer', 'place_id', 'score'])
    return data

    # todo consider making the df or numpy array here too.


def fake_data(place_1, place_2, data):
    # Code to try to set 0 as a score for all reviewers who didn't
    # review that book.
    reviewers = set(data.reviewer)
    for place in (place_1, place_2):
        for reviewer in reviewers:
            if reviewer not in data[data.place_id == place.id].reviewer.values:
                data = data.append({'reviewer': reviewer, 'place_id': place.id,
                                    'score': 0}, ignore_index=True)
    return data


def fake_data2(place_1, place_2, data):
    # Code to try to set 0 as a score for all reviewers who didn't
    # review that book.
    data = data.values
    reviewers = np.unique(data[:, 0])

    for place in (place_1, place_2):

        reviews = data[data[:, 1] == place.id]

        # Reviewers who didn't review it.
        didnt_review = np.setdiff1d(reviewers, reviews[:, 0])
        n = didnt_review.size

        addition = np.column_stack([didnt_review, np.repeat(place.id, n), np.zeros(n)])
        data = np.vstack([data, addition])

    return data


def correlate(place_1: Place, place_2: Place, data: pd.DataFrame):
    # todo got to speed this up.
    """Calculate the pearson correlation coefficient between two places."""
    datav = data.values

    data = fake_data(place_1, place_2, data)
    # return

    # Getting all the reviewers for these books
    place_1_reviewers = data[data.place_id == place_1.id].reviewer
    place_2_reviewers = data[data.place_id == place_2.id].reviewer

    # Look for common reviewers
    common_reviewers = set(place_1_reviewers).intersection(place_2_reviewers)

    # Let's extract the reviews for our 2 Harry potter books
    place_1_reviews = get_book_reviews(data, place_1.id, common_reviewers)
    place_2_reviews = get_book_reviews(data, place_2.id, common_reviewers)

    # We compute the Pearson Correlation Score
    correlation_coefficient = pearsonr(place_1_reviews.score, place_2_reviews.score)[0]

    # import brisk
    # correlation_coefficient = brisk.corr(place_1_reviews.score, place_2_reviews.score)

    # We know how they related
    return correlation_coefficient


# Let's create a function that collect the reviews of our common reviewers
def get_book_reviews(data, title, common_reviewers):
    reviewer_places = (data.reviewer.isin(common_reviewers)) & (data.place_id==title)
    reviews = data[reviewer_places].sort_values('reviewer')
    reviews = reviews[reviews.reviewer.duplicated() == False]
    return reviews


def find_similar(place1: Place) -> OrderedDict:
    """"""
    # todo way slow!
    reviews = find_reviews()

    scores = {place2: correlate(place1, place2, reviews) for place2 in Place.objects.all()}

    return OrderedDict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def find_similar_multiple(places: Iterable[Place]):
    """Accepts a list of strings containing place names.  Returns..."""
    similars = (find_similar(place) for place in places)

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


def find_db_entries(places: Iterable[str]):
    """Accept place name strings, as passed from a web form; find their
    corresponding database entries."""
    min_match_ratio = .8

    result = {}
    for place_name in places:
        ratios = []
        # todo this may be very slow
        for place in Place.objects.all():
            ratios.append((place, SequenceMatcher(None, place_name, place.city).ratio()))

        filtered = filter(lambda x: x[1] > min_match_ratio, ratios)
        matches = sorted(filtered, key=lambda x: x[1], reverse=True)

        # todo return only the top result for now.
        result[place_name] = matches[0]

        yield matches[0][0]

    # return {k: v[0] for k, v in result.items()}


def process_input(places: Iterable[str]):
    """Find recommendations based on input places."""
    entries = find_db_entries(places)

    return find_similar_multiple(entries)

