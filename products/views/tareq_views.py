from rest_framework import decorators, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.http import HttpRequest
from category import models as camodels
from products import models as pmodels, serializers as pserializer
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance


class ProductsFilterByLocationAndDistanceView(APIView):
    """
         An api to list products filtered by distance ordered for nearest to farthest.
         lat and lon are required
         ?latitude= & longitude= 
    """
    def get(self, request):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')

        if latitude and longitude:
            
            location = Point(float(longitude), float(latitude), srid=4326)
            
            products = pmodels.Product.objects.filter(service_provider_location__location__distance_lt=(location, 1000000)
            ).annotate(distance=Distance('service_provider_location__location', location)).order_by('distance')
            
            serializer = pserializer.ProudctSerializer(products, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Latitude and longitude parameters are required'}, status=status.HTTP_400_BAD_REQUEST)



@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny, ])
def product_filter_by_name(request:HttpRequest):
    """
        An api to list products filtered by it's name (ar & en)
        product name is required
        ?name=
    """
    product_name = request.query_params.get('name')
    
    if product_name:
        products = pmodels.Product.objects.filter(Q(en_title__icontains = product_name) | Q(ar_title__icontains=product_name)).distinct()
        if products:
            return Response(products.values('ar_title', 'en_title', 'price'))
        else:
            return Response({'error': 'No products found with that name'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Product name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)