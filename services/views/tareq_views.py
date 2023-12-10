from rest_framework import decorators, status, permissions
from rest_framework.response import Response
from django.db.models import Q
from django.http import HttpRequest
from services import models as smodels, serializers as sserializer
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_location(request: HttpRequest, pk: int):
    """
        An api to list services filtered by it's provider location
        pk is provider_location_id
    """
    language = request.META.get("Accept-Language")
    
    services = smodels.Service.objects.filter(provider_location=pk)
    serializer = sserializer.ServicesFilterSerializer(services, many=True, fields = {"language": language})
    
    if services:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({f"No provider location with id = {pk}"}, status = status.HTTP_404_NOT_FOUND)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_category(request: HttpRequest, pk: int):
    """
    An api to list services filtered in a specific category
    pk is category id
    """
    language = request.META.get("Accept-Language")
    services = smodels.Service.objects.filter(category=pk)
    
    if not services:
        return Response({"message": "No services found in this category"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = sserializer.ServicesFilterSerializer(services, many=True, fields = {"language":language})
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_distance(request: HttpRequest):
    """
        An api to list services filtered by distance ordered for nearest to farthest.
        lat and lon are required
        ?latitude=<integer> & longitude=<integer> 
    """    
    language = request.META.get("Accept-Language")
    
    latitude = request.query_params.get('latitude')
    longitude = request.query_params.get('longitude')

    if latitude and longitude:
    
        location = Point(float(longitude), float(latitude), srid=4326)
        
        services = smodels.Service.objects.filter(provider_location__location__distance_lt=(location, 1000000)
        ).annotate(distance=Distance('provider_location__location', location)
        ).order_by('distance')
        
        serializer = sserializer.ServicesFilterSerializer(services, many=True, fields = {'language':language})
        
        if services:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"No service provider in this area"}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Latitude and longitude parameters are required'}, status=status.HTTP_400_BAD_REQUEST)       


@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny, ])
def service_filter_by_name(request:HttpRequest):
    """
        An api to list services filtered by it's name (ar & en)
        services name is required
        ?name=<string>
    """
    language = request.META.get("Accepte-Language")
    
    service_name = request.query_params.get('name')
    
    if service_name:
    
        services = smodels.Service.objects.filter(Q(en_title__icontains = service_name) | Q(ar_title__icontains=service_name)).distinct()
        serializer = sserializer.ServicesFilterSerializer(services, many = True, fields = {"language": language})

        if services:
            return Response(serializer.data, status = status.HTTP_200_OK)
        else:
            return Response({'error': 'No services found with that name'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Service name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)