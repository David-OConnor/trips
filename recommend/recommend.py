from django.db.models import Q

from itertools import combinations
from typing import List, Tuple

import pandas as pd
from scipy.stats.stats import pearsonr

# from . import book_db
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


def do(place_1, place_2):
    reviews_ = []
    for i, submission in enumerate(Submission.objects.all()):
        for place in submission.places.all():
            reviews_.append(Review(i, place, 1))

    reviews2 = [(r.reviewer, r.place.city, r.score) for r in reviews_]
    data = pd.DataFrame(reviews2, columns=['reviewer', 'city', 'score'])

    # Code to try to set 0 as a score for all reviewers who didn't
    # review that book.
    reviewers = set(data.reviewer)

    for city in (place_1, place_2):
        for reviewer in reviewers:
            if reviewer not in data[data.city == city].reviewer.values:
                data = data.append({'reviewer': reviewer, 'city': city, 'score': 0},
                                   ignore_index=True)


    # Getting all the reviewers for these books
    place_1_reviewers = data[data.city == place_1].reviewer
    place_2_reviewers = data[data.city == place_2].reviewer

    # Look for common reviewers
    common_reviewers = set(place_1_reviewers).intersection(place_2_reviewers)

    # Let's extract the reviews for our 2 Harry potter books
    place_1_reviews = get_book_reviews(data, place_1, common_reviewers)
    place_2_reviews = get_book_reviews(data, place_2, common_reviewers)


    # We compute the Pearson Correlation Score
    correlation_coefficient = pearsonr(place_1_reviews.score, place_2_reviews.score)[0]

    # We know how they related
    return correlation_coefficient


# Let's create a function that collect the reviews of our common reviewers
def get_book_reviews(data, title, common_reviewers):
    reviewer_places = (data.reviewer.isin(common_reviewers)) & (data.city==title)
    reviews = data[reviewer_places].sort('reviewer')
    reviews = reviews[reviews.reviewer.duplicated()==False]
    return reviews


def find_similar(place):
    places = [p.city for p in Place.objects.all()]
    scores = {}

    for other_place in places:
        scores[other_place] = do(place, other_place)

    print(scores)
    from collections import OrderedDict
    return OrderedDict(sorted(scores.items(), key=lambda x: x[1], reverse=True))




#from
# def setup(books: List[Tuple[str, str]]):
#     result = []
#     for book in books:
#         works = book_db.query(book[0], book[1])
#         # Works being empty implies something matching your title and author
#         # was neither in the database, nor on Google's API.
#         if not works:
#             print("Can't find one of your entries", book[0], book[1])
#             continue
#         result.append(works[0])  # The best match.
#
#     return submit(result)
#
#
# def submit(books: List[Work]):
#     # todo this is a crude way of doing it that won't provide good results.
#     candidates = {}
#     for book in books:
#         rships = Relationship.objects.filter(Q(book1=book) | Q(book2=book))
#         for rship in rships:
#             # Determine which book is one we queried for; the other's the
#             # potential recommendation.
#             candidate = rship.book1 if rship.book2 == book else rship.book2
#
#             try:
#                 candidates[candidate] += rship.weight
#             except KeyError:
#                 candidates[candidate] = rship.weight
#
#     new_relationship(books)
#
#     # todo you want a ranked order; not just the top
#     best = max(candidates, key=lambda x: x['weight'])
#     return best
#
#
# def new_relationship(books):
#     # todo run after / async with book submission
#     for book1, book2 in combinations(books, 2):
#
#         # todo do it both orders, or force an alphabetic etc hierarchy
#         existing_relationship = Work.objects.filter(book1=book1)
#         # Using get here raises MultipleObjectsReturned if more than one relationship
#         # exists for this combination, as it should.
#         try:
#             existing_relationship = existing_relationship.get(book2=book2)
#         except Work.DoesNotExist:
#             relationship = Relationship(book1=book1, book2=book2)
#             relationship.save()
#         else:
#             existing_relationship.weight += 1






