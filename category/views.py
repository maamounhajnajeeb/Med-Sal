
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from category.serializers import CategorySerializer
from category.models import Category

class CategoryGet(APIView):
    serializer_class = CategorySerializer

    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = CategorySerializer(data=request.data)
   
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
   
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
   
    def delete(self, request):
        queryset = Category.objects.filter(name = 'Dental')
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    