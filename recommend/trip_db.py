from collections import namedtuple
import csv
import json
from typing import List, Iterator

import requests
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .models import Country, Region, Subregion, Place
from .private import mashape_key, goog_places_key


def get_all_countries() -> List[dict]:
    """Find countries from an API."""
    url = 'https://restcountries-v1.p.mashape.com/all'

    payload = {'X-Mashape-Key': mashape_key}

    result = requests.get(url, headers=payload)
    return result.json()


def get_all_places() -> Iterator[tuple]:
    """Find cities/places from a csv file."""
    # reference URL for worldcities.csv: http://www.opengeocode.org/download.php#cities
    with open('recommend/worldcities.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the column-definition row.

        for city in reader:
            # Cities in this csv may have multiple entries, in different languages.
            name_language = city[5]
            if name_language not in ['latin', 'english']:
                continue

            # US FIPS 5-2 1st level administrative division code (e.g., state/province).
            division_code = city[1]

            country_alpha2 = city[0].lower()
            city_name = city[6].lower()
            lat = city[7]
            lon = city[8]
            yield country_alpha2, division_code, city_name, lat, lon


def populate_places() -> None:
    """Populate the places table."""
    places = get_all_places()

    for city in places:
        country_alpha2, division_code, city_name, lat, lon = city

        # todo find better way to test for unicode compatibility.
        try:
            print(city_name)
        # Odd character in city name.
        except UnicodeEncodeError:
            continue
        try:
            country = Country.objects.get(alpha2=country_alpha2)
        except ObjectDoesNotExist:
            print("Can't find country in db: {}".format(country_alpha2))
            continue

        if division_code == '':
            division_code = 0

        place = Place(city=city_name, country=country, lat=lat, lon=lon,
                      division_code=division_code)

        try:
            place.save()
        # This wouldu come up for duplicate/similar entries in the csv, or if
        # the places table is already populated.
        except IntegrityError:
            continue


# get_place is currently unused.
def get_place(place_name: str):
    url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'

    payload = {'input': place_name,
               'key': goog_places_key}

    result = requests.get(url, params=payload)
    result = result.json()

    result2 = []
    for place in result['predictions']:
        if 'locality' in place['types']:  # 'locality'? 'political'
            result2.append(place)
    return result2


def populate_countries() -> None:
    """Populates the countries table."""
    countries_api = get_all_countries()

    for country_api in countries_api:
        region_name = country_api['region'].lower()
        subregion_name = country_api['subregion'].lower()

        region, created = Region.objects.get_or_create(name=region_name)

        # Some countries have a blank subregion; leave this as null rather than
        # setting as an empty string.  This is often for island nations.
        if subregion_name != '':
            subregion, created = Subregion.objects.get_or_create(name=subregion_name)
        else:
            subregion = None

        country = Country(name=country_api['name'].lower(),
                          region=region,
                          subregion=subregion,
                          alpha2=country_api['alpha2Code'].lower(),
                          alpha3=country_api['alpha3Code'].lower(),
                          )

        try:
            country.save()
        # Country already exists.
        except IntegrityError:
            pass


def remove_duplicates() -> None:
    """Remove duplicate places outside the US; ie only have one London, England,
       and one Paris, france. Duplicates in the USA are ok, due to state names."""
    for country in Country.objects.all():
        if country.name == 'united states':
            continue

        place_names = []
        for place in country.places.all():
            if place.city in place_names:
                print("Removed {}".format(place))
                place.delete()
            else:
                try:
                    place_names.append(place.city)
                except UnicodeEncodeError:
                    continue


def add_alternates() -> None:
    """Replace a country's alternate names with a dict within this file."""
    for country_name, alternates in alternate_names.items():
        country = Country.objects.get(name=country_name)
        country.alternate_names = json.dumps(alternates)
        country.save()


alternate_names = {
    'united kingdom': ['uk', 'england', 'britain', 'great britain'],
    'netherlands': ['the netherlands', 'holland'],
    'united states': ['usa', 'us', 'the united states', 'america'],
    'republic of ireland': ['ireland'],
    'republic of kosovo': ['kosovo'],
    'republic of macedonia': ['macedonia'],
    'democratic republic of the congo': ['congo'],
}




# Cities from some countries appear to be absent from the database. For example:
# China and vietname

china = Country.objects.get(alpha3='chn')
vietnam = Country.objects.get(alpha3='vnm')

manual_cities = [
    # Don't know the division_codes, so use 0 for all.
    Place(city='beijing', country=china, lat=39.916667, lon=116.383333, division_code=0),
    Place(city='chengdu', country=china, lat=30.658611, lon=104.064722, division_code=0),
    Place(city='shanghai', country=china, lat=31.2, lon=121.5, division_code=0),
    Place(city='hong kong', country=china, lat=22.3, lon=114.2, division_code=0),
    Place(city='macau', country=china, lat=22.166667, lon=113.55, division_code=0),
    Place(city='lhasa', country=china, lat=29.65, lon=91.116667, division_code=0),
    Place(city='shenzhen', country=china, lat=22.55, lon=114.1, division_code=0),

    Place(city='ho chi minh city', country=vietnam, lat=10.776889, lon=106.700806, division_code=0),
    Place(city='hanoi', country=vietnam, lat=21.028472, lon=105.854167, division_code=0),
    Place(city='can tho', country=vietnam, lat=10.033333, lon=105.783333, division_code=0),
    Place(city='da nang', country=vietnam, lat=16.066667, lon=108.233333, division_code=0),
    ]


def populate_manual_places() -> None:
    for place in manual_cities:
        try:
            place.save()
        except IntegrityError:
            print("{} already exists; not adding".format(place))
        else:
            print("Added manual city {}".format(place))


def populate():
    """Run all notable scripts in this file; set up a database from scratch."""
    populate_countries()
    populate_places()
    add_alternates()
    populate_manual_places()
    remove_duplicates()
