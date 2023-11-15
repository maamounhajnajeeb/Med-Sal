from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import decorators

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from . import serializers, helpers


Users = get_user_model()


class GroupView(viewsets.ModelViewSet):
    queryset = Group.objects
    permission_classes = ()
    serializer_class = serializers.GroupSerializer


class PermissionView(viewsets.ModelViewSet):
    queryset = Permission.objects
    permission_classes = ()
    serializer_class = serializers.PermissionSerializer


@decorators.api_view(["POST", ])
def assign_user_to_group(request: HttpRequest):
    
    user_id = request.data.get("user_id")
    user_instance = Users.objects.get(id=user_id)
    
    group_name = request.data.get("group_name")
    group = helpers.Groups(group_name)
    
    result = group.add_user(user=user_instance)
    
    return Response({
        "message": result
    }, status= status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
def assign_permission_to_group(request: HttpRequest):
    pass


@decorators.api_view(["POST", ])
def assign_permissions_to_group(request: HttpRequest):
    pass
