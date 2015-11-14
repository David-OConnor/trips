# This file contains python code represeting tags, including code to add database entries.

from django.db.models import Q

from .models import Place, Tag, Country, Subregion

place_tags = {
    ('cambridge', 'united kingdom'): ['university', 'historic'],
    ('miami', 'florida'): ['beach'],
    ('florence', 'italy'): ['art', 'historic'],
    ('london', 'england'): ['commercial', 'capital', 'major', 'culture'],
    ('washington', 'district of columbia'): ['capital', 'major'],
    ('paris', 'france'): ['capital', 'major', 'art', 'culture', 'food'],
    ('chania', 'greece'): ['beach'],
    ('dubai', 'united arab emirates'): ['commerce'],
    ('pisa', 'italy'):  ['art', 'mediterranean'],
    ('rome', 'italy'):  ['art', 'mediterranean', 'ancient', 'historeic'],
    ('copenhagen', 'denmark'):  [],
    ('helsinki', 'finland'): [],
    ('new york', 'new york'): ['commerce', 'major', 'art', 'dense', 'food'],
    ('new delhi', 'india'): ['culture', 'capital', 'major'],
    ('kraków', 'poland'): [],
    ('warsaw', 'poland'): ['capital'],
    ('marrakech', 'morocco'): [],
    ('siem reap', 'cambodia'): ['historic', 'ancient', 'genocide'],
    ('istanbul', 'turkey'): ['capital'],
    ('hanoi', 'vietnam'): ['historic'],
    ('prague', 'czech republic'): ['capital'],
    ('cape town', 'south africa'): ['beach'],
    ('zermatt', 'switzerland'): [],
    ('barcelona', 'spain'): ['mediterranean', 'culture', 'food'],
    ('goreme', 'turkey'): ['historic', 'ancient'],
    ('ubud', 'indonesia'): [],
    ('cusco', 'peru'): ['historic', 'ancient', 'mountains'],
    ('saint petersburg', 'russia'): ['historic', 'culture'],

}

# Country tags apply to all places in a country.  Do not include subregions
# that shadow model Subregions; this should be more specific.
country_tags = {
    'finland': ['nordic'],
    'denmark': ['nordic'],
    'sweden': ['nordic'],
    'iceland': ['nordic'],
    'norway': ['nordic'],
    'india': ['subcontinent'],
    'bangladesh': ['subcontinent'],
    'pakistan': ['subcontinent'],

}


def find_db_entry(place_name: str, country_name: str) -> Place:
    """Accept place name strings, as passed from a web form; find their
    corresponding database entries."""
    min_match_ratio = .5

    # todo this func needs polish
    ratios = []

    # todo us state
    db_place = Place.objects.get(Q(city=place_name), Q(country__name=country_name))
    return db_place
    #
    # # Q
    #
    # # Narrow the number of objects to filter with a startswith query.
    # for place in Place.objects.filter(city__istartswith=place_name[:3]):
    #     # Allow entries that include the country name, to help narrow down
    #     # the place.
    #
    #     if place.country.name == 'united states':
    #         db_place_name = ' '.join([place.city, place.state])
    #     else:
    #         db_place_name = ' '.join([place.city, place.country.name])
    #
    #     ratios.append((place, SequenceMatcher(
    #         None, place_name, db_place_name).quick_ratio()))
    #
    # filtered = filter(lambda x: x[1] > min_match_ratio, ratios)
    # matches = sorted(filtered, key=lambda x: x[1], reverse=True)
    #
    # # Find matches tied for the lead.
    # top_match = matches[0]


def make_tags():
    """Populate the database with tags based on a dict.  Create the tag entries
    if needed, and associate them with places."""
    for place_name, tag_names in place_tags.items():
        place = find_db_entry(*place_name)

        tags_db = []
        for tag_name in tag_names:
            # If this tag doesn't exist, create it.
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags_db.append(tag)

        place.tags.add(tags_db)
        place.save()


def make_subregions():
    """Populate the subregion field of models.Country entries."""
    for country_name, subregion_name in subregions.items():
        country = Country.get(name=country_name)
        subregion, created = Subregion.objects.get_or_create(name=subregion_name)
        country.subregion = subregion
        country.save()
