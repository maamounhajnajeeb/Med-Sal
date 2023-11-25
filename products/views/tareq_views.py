from rest_framework import decorators, status, permissions
from rest_framework.response import Response

from django.http import HttpRequest

from products import models, serializers




@decorators.permission_classes([permissions.AllowAny, ])
@decorators.api_view(['GET'])
def show_products_category(request: HttpRequest, pk):
    """
        Search only the products of a category
        api/v1/products/category/<int:pk>
        the PK is the category id
    """
    queryset = models.Product.objects.filter(category=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True)
    return Response(serializer.data, status = status.HTTP_200_OK)


