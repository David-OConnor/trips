from collections import defaultdict, OrderedDict
from difflib import SequenceMatcher
import json
from itertools import chain, islice
from typing import List, Iterable, Tuple, Generator, Iterator

import numpy as np
# from scipy.stats.stats import pearsonr

from django.db.models import Q

from .models import Place, Country, Submission


# todo scikit cosine similarity

def sort_by_key(data: dict):
    return OrderedDict(sorted(data.items(), key=lambda x: x[1], reverse=True))


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


def find_similar(place: Place, data: np.ndarray) -> OrderedDict:
    """Find similar places based on user submissions."""
    # Ignore this place if there are no existing submissions for it.
    if place.id not in data[:, 1]:
        return {}

    # todo use a filter for low, instead of no, review places.
    # Ignore places that have no reviewers.
    query = Place.objects.filter(id__in=data[:, 1])
    scores = {place2: correlate(place, place2, data) for place2 in query if place != place2}

    return scores


def find_similar_tagged(place: Place) -> OrderedDict:
    """This function is like find_similar, but uses tags and subregions to
    find related places rather than user-submitted data."""

    # use a set, since some tags may be duplicated between place and country.
    tags = set(chain(place.tags.all(), place.country.tags.all()))
    tag_ids = [tag.id for tag in tags]
    print("tags", tags)

    # Note: Places with no matching tags are filtered out, for speed.
    # If there's at least one matching place tag, that places country tags and
    # subregions count too.
    places_with_matching_tags = set(Place.objects.filter(tags__id__in=tag_ids))

    place_tag_data = defaultdict(int)
    for place2 in places_with_matching_tags:
        if place == place2:
            continue

        tags2 = set(chain(place2.tags.all(), place2.country.tags.all()))
        # Plus one for each matching tag.
        for tag in tags2:
            if tag in tags:
                place_tag_data[place2] += 1
        # Plus one for matching subregion.
        if place.country.subregion == place2.country.subregion:
            place_tag_data[place2] += 1

    return place_tag_data


def modulate_tagged(tag_results: OrderedDict) ->  OrderedDict:
    """Convert counts to a portion that can be compared with submission-based
    correlations."""
    # Input dict values are the number of common tags.
    multiplier = .05
    result = {k: v * multiplier for k, v in tag_results.items()}
    return result


def find_similar_multiple(similars: Iterable[OrderedDict]) -> OrderedDict:
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
    return result


def ratio_helper(place: Place, place_name, country_names) -> Iterator[Tuple[Place, float]]:
    for name in country_names:
        db_place_name = ' '.join([place.city, name])
        yield place, SequenceMatcher(None, name, db_place_name).quick_ratio()


def find_db_entry(place_name: str) -> Place:
    """Find the best match for an input string"""
    min_match_ratio = .7

    ratios = []
    # Narrow the number of objects to filter with a startswith query.
    for place in Place.objects.filter(city__istartswith=place_name[:3]):
        # Allow entries that include the country name, to help narrow down
        # the place.

        # todo clean up this if/else and use DRY if possible.
        if place.country.alternate_names:
            alternate_country_names = json.loads(place.country.alternate_names)

            alt_ratios = []
            for alt_name in alternate_country_names:
                db_place_name = ' '.join([place.city, alt_name])
                alt_ratios.append((place, SequenceMatcher(None, place_name, db_place_name).quick_ratio()))

            alt_matches = sorted(alt_ratios, key=lambda x: x[1], reverse=True)
            ratios.append(alt_matches[0])
        else:

            # todo improve this logic.
            # If there are no spaces in the name, no country was specified.
            if ' ' not in place_name:
                db_place_name = place.city
            elif place.country.name == 'united states':
                db_place_name = ' '.join([place.city, place.state])
            else:
                db_place_name = ' '.join([place.city, place.country.name])


            ratios.append((place, SequenceMatcher(
                None, place_name, db_place_name).quick_ratio()))

    filtered = filter(lambda x: x[1] > min_match_ratio, ratios)
    matches = sorted(filtered, key=lambda x: x[1], reverse=True)

    if not matches:
        return

    # Find matches tied for the lead.
    top_match = matches[0]
    tops = [m[0] for m in matches if m[1] == top_match[1]]

    # Find the most popular match of those tied for the lead.
    reviews = find_reviews()
    if not reviews:
        return top_match

    counts = [(place, (reviews[:, 1] == place.id).sum()) for place in tops]
    most_popular = max(counts, key=lambda x: x[1])

    return most_popular[0]



def find_db_entries(place_names: Iterable[str]) -> Tuple[List[Place], List[str]]:
    """Accept place name strings, as passed from a web form; find their
    corresponding database entries."""


    # todo if matches are identical or similar (florence italy vs usa), use
    # todo number of submissions to pick the most popular.
    entries, not_found = [], []

    for place_name in place_names:
        place = find_db_entry(place_name)

        if place:
            entries.append(place)
        else:
            not_found.append(place_name)

    return entries, not_found


def process_input(place_str: str):
    """Find recommendations based on input places. This function handles the
    overall processing, includes tweaks for web page display."""
    num_to_display = 10
    places = (place.strip() for place in place_str.split(','))

    entries, not_found = find_db_entries(places)
    entries = list(entries)

    # submit_new(entries)

    review_data = find_reviews()

    # Combine scores for reviews and tags
    similars = []
    for place in entries:

        similar = find_similar(place, review_data)
        similar_tag = find_similar_tagged(place)
        similar_tag = modulate_tagged(similar_tag)

        similar_combined = defaultdict(int)
        for place, review_score in similar.items():
            similar_combined[place] += review_score
        for place, review_score in similar_tag.items():
            similar_combined[place] += review_score

        similars.append(similar_combined)

    similars = find_similar_multiple(similars)
    similars = trim_output(similars, entries)

    similars = OrderedDict(islice(similars.items(), num_to_display))

    return similars, entries, not_found


def trim_output(similars, entries):
    """Removes computed recommendation results that are unsuitable for output."""
    # The top results will be the places submitted; remove them from the results.

    # Recommendations below this correlation value won't display.
    correlation_thresh = 0

    similars2 = {}
    for place, correlation in similars.items():
         # todo this line shoudl be uncessary based on checks upstream. Not working
         # todo upstream atm.
        if place not in entries and correlation > correlation_thresh:
        # if correlation > correlation_thresh:
            similars2[place] = correlation

    # todo you're calling OrderedDict 3 times, when you only need to once.
    return sort_by_key(similars2)


def submit_new(places: Iterable[Place]):
    """Creates a new submission of places someone likes.  Possibly called
    each time someone submits a form, or more for users with registered accounts."""
    places = list(places)

    # Submissions must include two places to correlate.
    if len(places) == 1:
        return

    print("Adding entries as a new submission.")
    submission = Submission()
    submission.save()
    for place in places:
        submission.places.add(place)
    submission.save()
