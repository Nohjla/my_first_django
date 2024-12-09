from django.urls import path, include
from .views import authView, home, user_logout, upload_file, dashboard, generate_url_view, validate_url_view, thank_you, archive_and_delete_view


urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path('upload/', upload_file, name="upload"),
    path("signup", authView, name="authView"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("logout_user", user_logout, name="logout"),
    path('generate-url/', generate_url_view, name='generate_url'),
    path('validate-url/', validate_url_view, name='validate_url'),
    path('thank_you/', thank_you, name='thank_you'),
    path('archive-and-delete/', archive_and_delete_view, name='archive_and_delete'),
]
