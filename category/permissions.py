from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            print("Safe method")
            return True
        
        if request.user.is_authenticated and request.user.user_type == "ADMIN":
            print("ADmin man")
        return request.user.is_authenticated and request.user.user_type == "ADMIN"