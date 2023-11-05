from django.contrib import admin
from .models import *
from django.contrib.gis.admin import OSMGeoAdmin

# @admin.register(ServiceProviderLocations)
# class ServiceProviderLocationsAdmin(OSMGeoAdmin):
#     default_lon = 100000
#     default_lat = 7495000
#     default_zoom = 10

admin.site.register(ServiceProvider)

admin.site.register(ServiceProviderLocations)
