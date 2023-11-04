from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework import viewsets, decorators

from .models import Category
from .permissions import IsAdmin
from .serializers import CategorySerializer

from users.models import UserIP
from utils.translate import get_translated


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
        resp = super().retrieve(request, *args, **kwargs)
        language = self.choose_lang()
        
        if language == "ar":
            name = resp.data["name"]
            resp.data["name"] = get_translated(name)
        
        return Response(
            resp.data
            , status=status.HTTP_200_OK
            , headers=self.get_success_headers(resp.data))
    
    def list(self, request, *args, **kwargs):
        """
        get all records, then see if there a change in language
        if there is a change, it translate the name attr
        """
        
        resp = super().list(request, *args, **kwargs)
        language = self.choose_lang()
        
        if language == "ar":
            for ordered_dict in resp.data:
                name = ordered_dict["name"]
                ordered_dict["name"] = get_translated(name)
        
        return Response(
            resp.data
            , status=status.HTTP_200_OK
            , headers=self.get_success_headers(resp.data))
    
    def choose_lang(self):
        """
        this function checking two things:
        1] if there is a language header 
        2] and if there is a record with the same IP Address
        
        if not 1] and 2] => return language from DB
        if 1] and 2] => update language from DB, then return it
        if 1] and not 2] => create UserIP model record, then return language
        
        """
        
        IP_Address = self.request.META.get("REMOTE_ADDR")
        language_code = self.request.headers.get("Accept-Language")
        obj = UserIP.objects.filter(ip_address=IP_Address)
        
        if obj.exists():
            obj = obj.first()
            if language_code:
                obj.language_code = language_code
                obj.save()
        
        elif not obj.exists():
            obj = UserIP.objects.create(
                ip_address=IP_Address
                , language_code=language_code)
        
        return obj.language_code
    
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
