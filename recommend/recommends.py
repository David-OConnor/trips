# For use by the django-recommends module.

from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from recommends.providers import RecommendationProvider
from recommends.providers import recommendation_registry

from .models import Place, Vote


class PlaceRecommendationProvider(RecommendationProvider):
    def get_users(self):
        return User.objects.filter(is_active=True, votes__isnull=False).distinct()

    def get_items(self):
        return Place.objects.all()

    def get_ratings(self, obj):
        return Vote.objects.filter(product=obj)

    def get_rating_score(self, rating):
        return rating.score

    def get_rating_site(self, rating):
        return rating.site

    def get_rating_user(self, rating):
        return rating.user

    def get_rating_item(self, rating):
        return rating.product

recommendation_registry.register(Vote, [Place], PlaceRecommendationProvider)


class MyProvider(PlaceRecommendationProvider):
    signals = ['django.db.models.post_save', 'django.db.models.pre_delete']

    def post_save(self, sender, instance, **kwargs):
        # Code that handles what should happen…
        pass

    def pre_delete(self, sender, instance, **kwargs):
        # Code that handles what should happen…
        pass