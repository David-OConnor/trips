from collections import defaultdict, OrderedDict
from difflib import SequenceMatcher
import json
from itertools import chain, islice
from typing import List, Iterable, Tuple, Generator, Iterator, Dict
import numpy as np
# from scipy.stats.stats import pearsonr

from django.db.models import Q

from .models import Place, Country, Submission, fips_5_2_codes


# todo latitude-based ranking?


# default_places avoids minor cities being defaulted to instead of more notable ones;
# ie london, alabama instead of london, united kingdom. todo Could be databse entries instead.
# todo uses a list to denote US state; consider using a tuple with True/False US flag instead
# todo for each entry.
default_places = {
    'auckland': 'new zealand',
    'arusha': 'tanzania',
    'athens': 'greece',
    'christchurch': 'new zealand',
    'dar es salaam': 'tanzania',
    'edmonton': 'canada',
    'london': 'united kingdom',
    'calgary': 'canada',
    'cambridge': 'united kingdom',
    'paris': 'france',
    'florence': 'italy',
    'pisa': 'italy',
    'brussels': 'belgium',
    'berlin': 'germany',
    'tokyo': 'japan',
    'delhi': 'india',
    'hong kong': 'china',
    'mexico city': 'mexico',
    # 'beijing': 'china',  # todo issue not finding chinese cities
    'cairo': 'egypt',
    'calcutta': 'india',
    'istanbul': 'turkey',
    'lagos': 'nigeria',
    # 'shanghai': 'china',# todo issue not finding chinese cities
    'karachi': 'pakistan',
    'mumbai': 'india',
    'moscow': 'russia',
    'jakarta': 'indonesia',
    'lima': 'peru',
    'bengaluru': 'india',
    'bangkok': 'thailand',
    'beijing': 'china',
    'tehran': 'iran',
    'baghdad': 'iraq',
    'dhaka': 'bangladesh',
    'ho chi minh city': 'vietnam',
    'hanoi': 'vietnam',
    'santiago': 'chile',
    'chennai': 'india',
    'abidjan': 'ivory coast',
    'durban': 'south africa',
    'nairobi': 'kenya',
    'ottawa': 'canada',
    'buenos aires': 'argentina',
    'copenhagen': 'denmark',
    'nice': 'france',
    'toulouse': 'france',
    'antwerp': 'belgium',
    'amsterdam': 'netherlands',
    'cardiff': 'united kingdom',
    'the hague': 'netherlands',
    'bristol': 'united kingdom',
    'kazan': 'russia',
    'rotterdam': 'netherlands',
    'seville': 'spain',
    'taipei': 'taiwan',
    'toronto': 'canada',
    'melbourne': 'australia',
    'montreal': 'canada',
    'newcastle': 'united kingdom',
    'warsaw': 'poland',
    'vienna': 'austria',
    'valencia': 'spain',
    'shanghai': 'china',
    'shenzhen': 'china',
    'sydney': 'australia',
    'perth': 'australia',
    'budapest': 'hungary',
    'stockholm': 'sweden',
    'wellington': 'new zealand',
    'winnipeg': 'canada',

    'washington': ['district of columbia'],
    'albuquerque': ['new mexico'],
    'anchorage': ['alaska'],
    'austin': ['texas'],
    'arlington': ['virginia'],
    'asheville': ['north carolina'],
    'atlanta': ['georgia'],
    'baltimore': ['maryland'],
    'boston': ['massachusetts'],
    'branson': ['missouri'],
    'chattanooga': ['tennessee'],
    'charleston': ['south carolina'],
    'charllotte': ['north carolina'],
    'colorado springs': ['colorado'],
    'chicago': ['illinois'],
    'dallas': ['texas'],
    'denver': ['colorado'],
    'destin': ['florida'],
    'fort lauderdale': ['florida'],
    'key west': ['florida'],
    'new york': ['new york'],
    'honolulu': ['hawaii'],
    'houston': ['texas'],
    'lahaina': ['hawaii'],
    'los angeles': ['california'],
    'indianapolis': ['indiana'],
    'miami': ['florida'],
    'milwaukee': ['wisconsin'],
    'memphis': ['tennessee'],
    'monterey': ['california'],
    'myrtle beach': ['south carolina'],
    'nashville': ['tennessee'],
    'new orleans': ['louisiana'],
    'kansas city': ['kansas'],
    'las vegas': ['nevada'],
    'oklahoma city': ['oklahoma'],
    'orlando': ['florida'],
    'palm springs': ['california'],
    'phoneix': ['arizona'],
    'park city': ['utah'],
    'portland': ['oregon'],
    'richmond': ['virginia'],
    'saint augustine': ['florida'],
    'san juan': ['puerto rico'],
    'san antonio': ['texas'],
    'saint louis': ['missouri'],
    'santa monica': ['california'],
    'salt lake city': ['utah'],
    'san diego': ['california'],
    'san francisco': ['california'],
    'santa fe': ['california'],
    'san jose': ['california'],
    'savannah': ['georgia'],
    'scottsdale': ['california'],
    'sedona': ['arizona'],
    'seattle': ['washington'],
    'tucson': ['arizona'],




}


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
    multiplier = .1
    return {k: v * multiplier for k, v in tag_results.items()}


def find_similar_multiple(similars: Iterable[OrderedDict]) -> Dict[Place, float]:
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


def process_default_place(place_name: str, default: dict) -> Place:
    """Finds a place object associated with a city name that's in default_places."""
    country_state = default[place_name]
    if isinstance(country_state, list):  # ie it's a US state.
        country_state = country_state[0]
        result = None
        for match in Place.objects.filter(city=place_name).filter(country='usa'):
            if match.state == country_state:
                result = match
                break
        if result is None:
            raise AttributeError("Problem with default US city logic")
        return result

    else:
        print(place_name, default[place_name])
        # This requires no duplicates exist; else an exception is raised.
        return Place.objects.get(Q(city=place_name),
                                 Q(country__name=default[place_name]))


def popularity_sort(matches: Iterable[Tuple[Place, float]]) -> Place:
    """Sort a series of places by most-reviewed."""
    reviews = find_reviews()
    if reviews is not None:
        return matches[0]

    counts = [(place, (reviews[:, 1] == place.id).sum()) for place in matches]
    most_popular = max(counts, key=lambda x: x[1])

    return most_popular[0]


def find_db_entry(place_name: str) -> Place:
    """Find the best match for an input search string."""
    place_name = place_name.lower()

    # Only check for an exact match if there's a space in the name.
    if ' ' in place_name:
        if place_name in default_places:
            return process_default_place(place_name, default_places)

    # Otherwise, check for closeness to one.
    else:
        # Save speed by utilizing an exact match if possible.
        if place_name in default_places:
            return process_default_place(place_name, default_places)

        closeness_to_default_thresh = .8
        for name, country in default_places.items():
            if name.startswith(place_name[:3]):
                closeness = SequenceMatcher(None, place_name, name).quick_ratio()
                if closeness > closeness_to_default_thresh:
                    return process_default_place(name, {name: country})

    min_match_ratio = .7
    words = place_name.split()
    ratios = []
    # Requiring the first three chars to match is rigid, but improves speed.
    potential_matches = Place.objects.filter(city__istartswith=place_name[:3])

    # todo this doesn't work for two-word cities!
    if len(words) == 1:  # city/town name specified only.
        for place in potential_matches:
            ratios.append((place, SequenceMatcher(
                None, place_name, place.city).quick_ratio()))

    else:
        country_names = []
        # country_alt names is a dict with format {alternate name: country name}
        country_alt_names = {}
        for country in Country.objects.all():
            country_names.append(country.name)
            if country.alternate_names:
                for alt_name in json.loads(country.alternate_names):
                    country_alt_names[alt_name] = country.alpha3

        state_names = fips_5_2_codes.keys()
        # todo don't require an exact match; instead of asking if it's equal, run
        # todo a sequencematcher on and make sure it passes a thresh?
        # Assume the first word is the city, or at least part of it.
        for i, word in enumerate(words[1:]):
            # Match against a city name; assume the city is the words up to,
            # but not including the one that triggered this country or state match.
            # Use i + 1 in the index, since you're skipping the first index in
            # the for loop.
            city_name_guess = ' '.join(words[:i + 1])
            entry_name_guess = ' '.join([city_name_guess, word])

            if word in country_names:
                for place in potential_matches.filter(country__name=word):

                    db_name_guess = ' '.join([place.city, place.country.name])
                    ratios.append((place, SequenceMatcher(
                        None, entry_name_guess, db_name_guess).quick_ratio()))

            elif word in country_alt_names:
                for place in potential_matches.filter(country=country_alt_names[word]):
                    db_name_guess = ' '.join([place.city, word])
                    ratios.append((place, SequenceMatcher(
                        None, entry_name_guess, db_name_guess).quick_ratio()))

            elif word in state_names:
                for place in potential_matches.filter(country='usa'):
                    if place.state == word:
                        db_name_guess = ' '.join([place.city, place.state])
                        ratios.append((place, SequenceMatcher(
                            None, entry_name_guess, db_name_guess).quick_ratio()))

        for place in potential_matches:
            # Skip if we already added it after guessing the right country.
            if place in [r[0] for r in ratios]:
                continue

            if place.country.alpha3 == 'usa':
                country_state = place.state
            else:
                country_state = place.country.name

            db_name_guess = ' '.join([place.city, country_state])
            ratios.append((place, SequenceMatcher(
                None, place_name, db_name_guess).quick_ratio()))

    # Remove low-quality matches, and sort by highest match.
    filtered = filter(lambda x: x[1] > min_match_ratio, ratios)
    matches = sorted(filtered, key=lambda x: x[1], reverse=True)

    if not matches: # Didn't find anything.
        return

    # Find matches tied for the lead.
    top_match = matches[0]
    tops = [m[0] for m in matches if m[1] == top_match[1]]

    # Find the most popular match of those tied for the lead.
    return popularity_sort(tops)


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

    submit_new(entries)

    review_data = find_reviews()

    scores_tag = []
    scores_user = []
    for input_place in entries:
        similar_tag = find_similar_tagged(input_place)
        scores_tag.append(modulate_tagged(similar_tag))

        if review_data is not None:
            scores_user.append(find_similar(input_place, review_data))

    # composite implies a score using all input places; combined means using
    # both tag and user data.
    composite_tag = find_similar_multiple(scores_tag)
    composite_user = find_similar_multiple(scores_user)


    combined_composites = defaultdict(float)
    for place, score in composite_tag.items():
        combined_composites[place] += score
    for place, score in composite_user.items():
        combined_composites[place] += score

    composite_tag = sort_by_key(composite_tag)
    composite_user = sort_by_key(composite_user)
    combined_composites = sort_by_key(combined_composites)


    combined_composites = trim_output(combined_composites, entries)
    # Sort by score, and only show the top X entries.
    combined_composites = OrderedDict(islice(combined_composites.items(), num_to_display))

    return combined_composites, composite_tag, composite_user, entries, not_found


def trim_output(similars: Dict[Place, float], entries: List[Place]):
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
