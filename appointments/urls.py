from django.urls import re_path, path

from appointments.views import draft_views, appointments_views, rejected_views

app_name = "appointments"


urlpatterns = [
    path("draft/add/", draft_views.CreateDraft.as_view(), name="create_draft"),
    
    path("draft/<int:pk>/", draft_views.RUDDraft.as_view(), name="read_update_delete_draft"),
    
    path("drafts/", draft_views.all_drafts, name="all_drafts"),
    
    path("drafts/provider/", draft_views.provider_drafts, name="provider_drafts"),
    
    path("drafts/user/", draft_views.user_drafts, name="user_drafts"),
    
]
