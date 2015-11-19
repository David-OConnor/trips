# This file contains python code represeting tags, including code to add database entries.
from collections import namedtuple

# usa is a bool. If True, country_state is a state; else a country.
TagKey = namedtuple('TagKey', ['city', 'country_state', 'usa'])


from django.db.models import Q

from .models import Place, Tag, Country, CountryTag


place_tags = {
    TagKey('cambridge', 'united kingdom', False): ['university', 'historic'],
    TagKey('valetta', 'malta', False): ['mediterranean', 'island', 'beach', 'scenic',
                                        'culture'],
    TagKey('florence', 'italy', False): ['art', 'historic', 'culture', 'tuscany'],
    TagKey('milan', 'italy', False): ['culture' 'art'],
    TagKey('pisa', 'italy', False):  ['art', 'mediterranean', 'tuscany'],
    TagKey('rome', 'italy', False):  ['art', 'mediterranean', 'ancient', 'historic',
                                      'capital'],
    TagKey('london', 'united kingdom', False): ['commercial', 'capital', 'major', 'culture'],
    TagKey('louisville', 'kentucky', True): ['alcohol', 'southern us'],
    TagKey('washington', 'district of columbia', True): ['capital', 'major'],
    TagKey('philadelphia', 'pennsylvania', True): ['historic'],
    TagKey('las vegas', 'nevada', True): ['gambling, modern, nightlife', 'theater'],
    TagKey('houston', 'texas', True): ['southern us'],
    TagKey('maui', 'hawaii', True): ['beach', 'tropical', 'island', 'coastal',
                                     'resort'],
    TagKey('austin', 'texas', True): ['southern us'],
    TagKey('cleveland', 'texas', True): ['southern us'],
    TagKey('atlanta', 'georgia', True): ['southern us'],
    TagKey('miami', 'florida', True): ['beach'],
    TagKey('orlando', 'florida', True): ['beach', 'resort', 'children', 'amusement'],
    TagKey('new york', 'new york', True): ['commerce', 'major', 'art',
                                           'dense', 'food', 'coastal'],
    TagKey('catskills', 'new york', True): ['hipster', 'nature'],
    TagKey('salt lake city', 'utah', True): ['western us', 'nature'],
    TagKey('wasatch mountains', 'utah', True): ['moutnains', 'ski', 'resort'],
    TagKey('paris', 'france', False): ['capital', 'major', 'art', 'culture', 'food'],
    TagKey('chaniá', 'greece', False): ['beach', 'coastal', 'crete'],
    TagKey('réthymno', 'greece', False): ['beach', 'coastal', 'crete'],
    TagKey('athens', 'greece', False): ['beach', 'coastal', 'historic', 'culture', 'art'],
    TagKey('dubai', 'united arab emirates', False): ['commerce', 'modern', 'coastal',
                                                     'beach'],
    TagKey('abu dhabi', 'united arab emirates', False): ['capital', 'modern', 'coastal',
                                                         'beach'],
    TagKey('muscat', 'oman', False):  ['capital', 'ancient'],
    TagKey('leipzig', 'germany', False):  ['art', 'music', 'historic'],
    TagKey('copenhagen', 'denmark', False):  [],
    TagKey('helsinki', 'finland', False): [],
    TagKey('new delhi', 'india', False): ['culture', 'capital', 'major'],
    TagKey('kraków', 'poland', False): [],
    TagKey('warsaw', 'poland', False): ['capital', 'culture'],
    TagKey('puerto plata', 'dominican republic', False): ['beach', 'coastal, resort',
                                                          'tropical'],
    TagKey('marrakech', 'morocco', False): ['culture'],
    TagKey('fez', 'morocco', False): [],
    TagKey('siem reap', 'cambodia', False): ['historic', 'ancient', 'genocide'],
    TagKey('istanbul', 'turkey', False): ['capital', 'culture', 'coastal'],
    # Cant' find any cities in vietnam
    # TagKey('hanoi', 'vietnam', False): ['historic'],
    TagKey('prague', 'czech republic', False): ['capital'],
    TagKey('cape town', 'south africa', False): ['beach'],
    TagKey('johannesburg', 'south africa', False): ['wildlife', 'resort'],
    # Cant' find zermatt
    # TagKey('zermatt', 'switzerland', False): [],
    TagKey('barcelona', 'spain', False): ['mediterranean', 'culture', 'food'],
    # Can't find goreme in db
    # TagKey('goreme', 'turkey', False): ['historic', 'ancient'],
    TagKey('ubud', 'indonesia', False): [],
    TagKey('bali', 'indonesia', False): ['rainy', 'tropical', 'culture', 'island'],
    TagKey('jakarta', 'indonesia', False): ['coastal', 'commerce', 'modern'],
    TagKey('rotterdam', 'the netherlands', False): ['culture', 'major', 'art',
                                                    'coastal'],
    TagKey('cusco', 'peru', False): ['historic', 'ancient', 'mountains'],
    TagKey('hokkaido', 'japan', False): ['ski', 'mountains'],
    TagKey('tokyo', 'japan', False): ['historic', 'ancient', 'culture', 'capital',
                                      'major', 'commerce'],
    TagKey('saint petersburg', 'russia', False): ['historic', 'culture'],
    TagKey('bangkok', 'thailand', False): ['major', 'culture'],
    TagKey('kathmandu', 'nepal', False): ['scenic'],
    TagKey('budapest', 'hungary', False): ['capital', 'major', 'culture'],
    TagKey('queenstown', 'new zealand', False): ['scenic', 'mountains'],
    TagKey('hong kong', 'china', False): ['major', 'commerce'],
    TagKey('chengdu', 'china', False): ['wildlife', 'commerce', 'culture'],
    TagKey('sydney', 'austalia', False): ['major', 'coastal', 'commerce', 'beach'],
    TagKey('canberra', 'austalia', False): ['capital', 'coastal'],
    TagKey('rio de janeiro', 'brazil', False): ['major', 'coastal', 'beach', 'scenic',
                                                'coastal'],
    TagKey('', '', False): [],
    TagKey('', '', False): [],
    TagKey('', '', False): [],
    TagKey('', '', False): [],

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


def find_db_entry(place: TagKey) -> Place:
    """Accept place name strings, as passed from a web form; find their
    corresponding database entries."""

    if place.usa:
        result = Place.objects.filter(city=place.city).filter(country__name='united states')
        for place2 in result:
            if place2.state == place.country_state:
                result = place2
                break
        if not result:
            raise AttributeError("UHOH, no result on {}".format(place))
        return result

    # Multiple paris entries; use filter...[0] instead of get fo rnow.
    # return Place.objects.get(Q(city=place.city), Q(country__name=place.country_state))
    return Place.objects.filter(Q(city=place.city), Q(country__name=place.country_state))[0]



def make_tags():
    """Populate the database with tags based on a dict.  Create the tag entries
    if needed, and associate them with places."""
    for tag_key, tag_names in place_tags.items():
        print(tag_key.city, tag_key.country_state)
        place = find_db_entry(tag_key)

        for tag_name in tag_names:
            # If this tag doesn't exist, create it.
            tag, created = Tag.objects.get_or_create(name=tag_name)
            place.tags.add(tag)
        place.save()


def make_country_tags():
    """Populate the subregion field of models.Country entries."""
    for country_name, tag_names in country_tags.items():
        country = Country.objects.get(name=country_name)
        for tag_name in tag_names:
            tag, created = CountryTag.objects.get_or_create(name=tag_name)
            country.tags.add(tag)
        country.save()
