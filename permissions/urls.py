from django.urls import path

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("groups", views.GroupView, basename="group_view")
router.register("permissions", views.PermissionView, basename="permission_view")

app_name = "permissions"

urlpatterns = [
    
]

urlpatterns += router.urls