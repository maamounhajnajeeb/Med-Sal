from rest_framework import viewsets, decorators
from rest_framework import status, filters
from rest_framework.response import Response

from .models import Category
from .permissions import IsAdmin
from .serializers import CategorySerializer


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
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = self.change_serializer_data(serializer.data)
        return Response(data)
    
    def change_serializer_data(self, data):
        data["name"] = data["name"]["langs"][self.request.LANGUAGE_CODE]
        return data
    
    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        for counter in range(len(resp.data)):
            obj = resp.data[counter]
            resp.data[counter] = self.change_serializer_data(obj)
        
        return Response(
            resp.data, status=resp.status_code
            , headers=self.get_success_headers(resp.data))
    
    def perform_create(self, serializer):
        """
        edit the pre-built function just to return the model instance after saving
        """
        return serializer.save()
    
    def get_parent(self, parent_parameter):
        parent_parameter = int(parent_parameter)
        parent_instance = Category.objects.get(id=parent_parameter)
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
            child_instance = Category.objects.select_related("parent").get(id=int(self.kwargs["pk"]))
            self.assign_parent(parent_parameter, child_instance)
        return super().update(request, *args, **kwargs)


@decorators.api_view(["GET", ])
def parent_sub_category(request, pk):
    queryset = Category.objects.filter(parent=pk)
    serialized_data = CategorySerializer(queryset, many=True)
    return Response(
        serialized_data.data
        , status=status.HTTP_200_OK)