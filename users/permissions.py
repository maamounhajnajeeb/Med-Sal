from rest_framework import permissions

from django.http import HttpRequest

class IsAdminOrOwner(permissions.BasePermission):
    
    def has_permission(self, request: HttpRequest, view):
        return request.user.is_authenticated
        
    def has_object_permission(self, request: HttpRequest, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return request.user == obj or request.user.is_staff
