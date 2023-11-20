from rest_framework import permissions

from django.http import HttpRequest


"""
- Admins Permissions (staff user):
    - Modify any service_provider data 
    - Have access to all service_providers data
    - Can retrieve a specific service_provider data using his (ID)
    - Change account status for a service_provider 

- Authenticated users permissions:
    - Retrieve a specific service_provider data using his (ID)
    - An authenticated user logged in as a service_provider can update his own data 

- Not Authenticated users permissions:
    - Can login as a service_provider (Create a new service_provider)
"""

# Permissions for Get and Post 
class OnlyAdminsCanListPermissions(permissions.BasePermission):
    def has_permission(self, request, view):        
        # Check if the requested method is in safe_methods(List), apply permission that only admins have access to it
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff
    

# Permissions for Patch and Retrieve
class UpdateAndRetrievePermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the requested method is in safe_methods(Retrieve), apply permission that only authenticated users have access to it
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Check if the requested method is not in safe_methods(Patch/Update), apply permission that only admins have access to it or a service provider on his own data
        else:
            return obj.user.id == request.user.id or request.user.is_staff


class UpdateAccountPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return obj.user.id 
        else:
            return False


class UnAuthenticated(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view):
        return not request.user.is_authenticated
    