from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework import decorators

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

from . import serializers, helpers


Users = get_user_model()


class ContentTypeView(viewsets.ModelViewSet):
    queryset = ContentType.objects
    serializer_class = serializers.ContentTypeSerializer
    permission_classes = (IsAdminUser, )
    
    def create(self, request, *args, **kwargs):
        return Response({"message": "This method isn't allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def destroy(self, request, *args, **kwargs):
        return Response({"message": "This method isn't allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def update(self, request, *args, **kwargs):
        return Response({"message": "This method isn't allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GroupView(viewsets.ModelViewSet):
    queryset = Group.objects
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.GroupSerializer


class PermissionView(viewsets.ModelViewSet):
    queryset = Permission.objects
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.PermissionSerializer


@decorators.api_view(["GET", ])
@decorators.permission_classes([IsAdminUser, ])
def group_permissions(request, pk: int):
    group = helpers.Groups()
    queryset = group.get_permissions(group_id=pk)
    
    serializer = serializers.GroupSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([IsAdminUser, ])
def get_user_group(request: Request, pk):
    group = helpers.Groups()
    query_set = group.get_user_groups(pk)
    
    serializer = serializers.GroupSerializer(query_set, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["DELETE", ])
@decorators.permission_classes([IsAdminUser, ])
def execlude_user_from_group(req: Request):
    user_id, group_id = req.query_params.get("user_id"), req.query_params.get("group_id")
    if not (user_id and group_id):
        return Response({"message": "You should add group_id & user_id in the request query params"}
            , status=status.HTTP_400_BAD_REQUEST)
    
    group = helpers.Groups()
    result = group.delete_user_from_group(user_id=user_id, group_id=group_id)
    
    return Response({"message": result}, status=status.HTTP_204_NO_CONTENT)


@decorators.api_view(["POST", ])
@decorators.permission_classes([IsAdminUser, ])
def assign_user_to_group(req: Request):
    user_id, group_id = req.query_params.get("user_id"), req.query_params.get("group_id")
    if not (user_id and group_id):
        return Response({"message": "You should add group_id & user_id in the request query params"}
            , status=status.HTTP_400_BAD_REQUEST)
    
    group = helpers.Groups()
    result = group.add_user(user_id=int(user_id), group_id=int(group_id))
    
    return Response({"message": result}, status= status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
@decorators.permission_classes([IsAdminUser, ])
def assign_permission_to_group(req: Request):
    permission_id, group_id = req.query_params.get("permission_id"), req.query_params.get("group_id")
    if not (permission_id and group_id):
        return Response({"Error": "both permission_id and group_id needed to be in the query params"}
            , status=status.HTTP_400_BAD_REQUEST)
    
    group = helpers.Groups()
    result = group.add_permission(perm_id=int(permission_id), group_id=int(group_id))
    
    return Response({
        "message": result
    }, status=status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
@decorators.permission_classes([IsAdminUser, ])
def assign_permissions_to_group(req: Request):
    permission_ids, group_id = req.query_params.get("permission_ids"), req.query_params.get("group_id")
    if not (permission_ids and group_id):
        return Response({"Error": "both permission_ids and group_id needed to be in the query params"}
            , status=status.HTTP_400_BAD_REQUEST)
    
    group = helpers.Groups()
    result = group.add_permissions(
        group_id=int(group_id), perms_ids=[int(perm) for perm in permission_ids.split(",")])
    
    return Response({
        "message": result
    }, status=status.HTTP_201_CREATED)
