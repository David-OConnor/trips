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

    # US FIPS 5-2 1st level administrative division code (e.g., state/province)
    division_code = models.CharField(max_length=2)

    def __str__(self):
        return ', '.join([self.city, self.country.name])

    class Meta:
        unique_together = ('city', 'country', 'division_code')


class Submission(models.Model):
    """An entry from one anonymous submission of several liked places."""
    places = models.ManyToManyField(Place)