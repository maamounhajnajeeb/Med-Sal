from django.urls import re_path, path

from services.views import maamoun_views, tareq_views

app_name = "services"

urlpatterns = [
    # create service
    path("create/", maamoun_views.CreateService.as_view(), name="create_service"),
    
    # rud services
    path("<int:pk>/", maamoun_views.ServiceRUD.as_view(), name="service_rud"),
    
    # all services
    path("", maamoun_views.ListAllServices.as_view(), name="all_services"),

    # list services by name
    path("servicename/", tareq_views.service_filter_by_name, name="service_by_name"),

    # list service by provider location pk is provider id
    path("location/<int:pk>", tareq_views.services_by_location, name="service_by_location"),

    # list services by distance
    path("distance/", tareq_views.services_by_distance, name="service_by_distance"),

    # list services in a category pk is category id
    path("category/<int:pk>", tareq_views.services_by_category, name="service_for_category"),
]
