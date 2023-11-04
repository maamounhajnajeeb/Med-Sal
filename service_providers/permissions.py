from rest_framework.permissions import SAFE_METHODS
from rest_framework import permissions

class ListAndCreatePermissions(permissions.BasePermission):
    def has_permission(self, request, view):        
        if request.method in SAFE_METHODS:
            return request.user.is_staff
        else:
            return not request.user.is_authenticated


class UpdateAndDeletePermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return obj.user.id == request.user.id or request.user.is_staff

