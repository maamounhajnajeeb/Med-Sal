from django.urls import path

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("groups", views.GroupView, basename="group_view")
router.register("permissions", views.PermissionView, basename="permission_view")

app_name = "permissions"

urlpatterns = [
    path("groups/join_user/", views.assign_user_to_group, name="assign_user_to_group"),
    path("groups/add_permission/", views.assign_permission_to_group, name="assign_permission_to_group"),
    path("groups/add_permissions/", views.assign_permissions_to_group, name="assign_permissions_to_group"),    
]

urlpatterns += router.urls