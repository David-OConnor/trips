from django.contrib import admin

from .models import Place, Country, Submission, Region, Subregion, Tag, NotFound

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('city', 'country')

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'alpha3')

class SubmissionAdmin(admin.ModelAdmin):
    fields = ('places',)
    pass

class RegionAdmin(admin.ModelAdmin):
    pass

class SubregionAdmin(admin.ModelAdmin):
    pass

class TagAdmin(admin.ModelAdmin):
    pass

class NotFoudnAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')


admin.site.register(Place, PlaceAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Subregion, SubregionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(NotFound, NotFoudnAdmin)