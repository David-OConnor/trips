from django.contrib.auth.models import User
from django.db import models


# regions are places like 'africa', 'middle_east', 'western_europe' etc
class Region(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Country(models.Model):
    name = models.CharField(max_length=30, unique=True)
    region = models.ForeignKey(Region, related_name='countries')


class Place(models.Model):
    city = models.CharField(max_length=50)
    # country = models.CharField(max_length=50)
    country = models.ForeignKey(Country, related_name='places')

    # def __str__(self):
    #     return self.city

    class Meta:
        unique_together = ('city', 'country')


class Vote(models.Model):
    """A Vote on a Product"""
    user = models.ForeignKey(User, related_name='votes')
    place = models.ForeignKey(Place)
    # site = models.ForeignKey(Site)
    # score = models.FloatField()

    def __str__(self):
        return "Vote"


class Submission(models.Model):
    """An entry from one anonymous submission"""
    places = models.ManyToManyField(Place)


class Similarity:
    """Boilerplate for django-recommends"""
    object = models.ForeignKey(Place)
    related_object = models.ForeignKey(Place)
    score = models.FloatField(default=0)

    def __str__(self):
        return "Similiarity. Place 1: {}, Place 2: {}".format(self.object, self.related_object)
    #
    # class Meta:
    #     # todo this may allow duplicates of opposite order.  Investigate.
    #     unique_together = ('place1d', 'place2')


class Reccomendation:
    """Boilerplate for django-recommends"""
    object = models.ForeignKey(Place)
    user = None
    score = models.FloatField(default=0)




# class Relationship(models.Model):
#     """Defines a relationship between two books.  For example, if someone lists
#     liking three books, a relatinship would be created for book1-2, 1-3, and 2-3.
#     If any of these exist, their count would increase."""
#     place1 = models.ForeignKey(Place)
#     place2 = models.ForeignKey(Place)
#     weight = models.IntegerField(default=0)
#
#     def __str__(self):
#         return "Relationship. Place 1: {}, Place 2: {}".format(self.place1, self.placd2)
#
#     class Meta:
#         # todo this may allow duplicates of opposite order.  Investigate.
#         unique_together = ('place1d', 'place2')