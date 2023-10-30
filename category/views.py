from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.response import Response

from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
from django.shortcuts import render

from .models import Category
from .permissions import IsAdmin
from .serializers import CategorySerializer


def home(request):
    return render(request, "home.html", {})


class CRUDCategory(viewsets.ModelViewSet):
    """
    path : "api/v1/category/"
    
    this view offers four api methods
    
    every body method: get method
    admins methods: post, update[patch, put] and delete methods
    
    you can call specific category by its id
    also you can search for specific category by its name (via api/v1/category?serach=<category_name>)
    
    you can assign parent category for each sub category by using parent in the form data
    create and update methods accept parent as [integer id, string name]
    
    """
    serializer_class = CategorySerializer
    queryset = Category.objects
    permission_classes = (IsAdmin, )
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", ]
    
    def perform_create(self, serializer):
        return serializer.save()
    
    def get_parent(self, parent_parameter):
        try:
            parent_parameter = int(parent_parameter)
            parent_instance = Category.objects.get(id=parent_parameter)
        except:
            parent_instance = Category.objects.get(name=parent_parameter)
        return parent_instance
    
    def assign_parent(self, parent_parameter, child_instance):
        parent_instance = self.get_parent(parent_parameter)
        child_instance.parent = parent_instance
        child_instance.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        child_instance = self.perform_create(serializer)
        
        if request.data.get("parent"):
            parent_parameter = request.data.get("parent")
            self.assign_parent(parent_parameter, child_instance)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def update(self, request, *args, **kwargs):
        if request.data.get("parent"):
            parent_parameter = request.data["parent"]
            child_instance = Category.objects.select_related("parent").get(id=self.kwargs["pk"])
            self.assign_parent(parent_parameter, child_instance)
        return super().update(request, *args, **kwargs)
