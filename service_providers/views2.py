from rest_framework import viewsets
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ServiceProvider, ServiceProviderLocations
from .serializers import ServiceProviderSerializer, ServiceProviderLocationSerializer, CalculateDistanceSerializer
import geopy.distance
from .permissions import UpdateAndRetrievePermissions, ListAndCreatePermissions



"""

    - Not Authenticated users can create a new service_provider POST request (Done)
    - Only admins can list all service_providers data GET request (Done)

"""