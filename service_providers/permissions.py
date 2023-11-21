from rest_framework import permissions

class UpdateRequestsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS or request.method == 'PATCH':
            return request.user.is_staff
       
        elif request.method == 'POST':
            return request.user.is_authenticated
       
        else:
            return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method == 'DELETE':
            return request.user.is_staff
        
