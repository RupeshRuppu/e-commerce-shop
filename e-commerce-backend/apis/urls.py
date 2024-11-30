from django.urls import path
from .views import profile_upload

urlpatterns = [
    path("profile-upload/", profile_upload),
]
