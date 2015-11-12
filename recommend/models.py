from django.contrib.auth.models import User
from django.db import models


# regions are places like 'africa', 'middle_east', 'western_europe' etc
class Region(models.Model):
    # todo possibly use subregions as well.
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    region = models.ForeignKey(Region, related_name='countries')
    # ISO 3166-1 alpha-2 and alpha-3 country codes
    # todo consider removing alpha 3, and making alpha 2 the primary key.
    alpha2 = models.CharField(max_length=2, unique=True)
    alpha3 = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return self.name


class Place(models.Model):
    city = models.CharField(max_length=100)
    # country = models.CharField(max_length=50)
    country = models.ForeignKey(Country, related_name='places')
    lat = models.FloatField()
    lon = models.FloatField()
    # priority allows choosing a default between multiple cities with the same name.
    # priority = models.IntegerField()

    # US FIPS 5-2 1st level administrative division code (e.g., state/province)
    division_code = models.CharField(max_length=2)

    @property
    def state(self):
        # Only produces meaningful data for the US.
        return codes2[int(self.division_code)]

    def __str__(self):
        if self.country.name == 'united states':
            return ', '.join([self.city, self.state, self.country.name])
        else:
            return ', '.join([self.city, self.country.name])

    class Meta:
        unique_together = ('city', 'country', 'division_code')


class Submission(models.Model):
    """An entry from one anonymous submission of several liked places."""
    places = models.ManyToManyField(Place)



fips_5_2_codes = {
    'alabama': 1,
    'alaska': 2,
    'american Samoa': 60,
    'american Samoa2': 3,
    'arizona':	4,
    'arkansas': 5,
    'baker Island': 81,
    'california': 6,
    'canal Zone': 7,
    'colorado': 8,
    'connecticut': 9,
    'delaware': 10,
    'district of Columbia': 11,
    'florida': 12,
    'federated States of Micronesia': 64,
    'georgia':	13,
    'guam':	66,
    'guam2': 14,
    'hawaii': 15,
    'howland Island': 84,
    'idaho 	ID': 16,
    'illinois': 17,
    'indiana': 18,
    'iowa': 19,
    'jarvis Island': 86,
    'johnston Atoll': 67,
    'kansas': 20,
    'kentucky': 21,
    'kingman Reef': 89,
    'louisiana': 22,
    'maine': 23,
    'marshall Islands': 68,
    'maryland': 24,
    'massachusetts': 25,
    'michigan': 26,
    'midway Islands': 71,
    'minnesota': 27,
    'mississippi': 28,
    'missouri': 29,
    'montana': 30,
    'navassa': 76,
    'nebraska': 31,
    'nevada': 32,
    'new Hampshire': 33,
    'new Jersey': 34,
    'new Mexico': 35,
    'new York': 36,
    'north Carolina': 37,
    'north Dakota': 38,
    'northern Mariana Islands': 69,
    'Ohio': 39,
    'Oklahoma': 40,
    'Oregon': 41,
    'Palau': 70,
    'Palmyra Atoll': 95,
    'Pennsylvania':	42,
    'Puerto Rico': 43,
    'Puerto Rico2': 72,
    'Rhode Island': 44,
    'South Carolina': 45,
    'South Dakota':	46,
    'Tennessee': 47,
    'Texas': 48,
    'U.S. Minor Outlying Islands': 74,
    'Utah':	49,
    'Vermont': 50,
    'Virginia':	51,
    'Virgin Islands of the U.S.': 78,
    'Virgin Islands of the U.S.2': 52,
    'Wake Island': 79,
    'Washington': 53,
    'West Virginia': 54,
    'Wisconsin': 55,
    'Wyoming': 56,
}

# todo temp reversal; fix the above instead.
codes2 = {v: k.lower() for k, v in fips_5_2_codes.items()}
