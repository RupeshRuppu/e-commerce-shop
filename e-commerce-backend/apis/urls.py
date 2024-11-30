from django.urls import path
from .views import profile_upload, product_upload

urlpatterns = [
    path("profile-upload/", profile_upload),
    path("product-upload/", product_upload),
]
