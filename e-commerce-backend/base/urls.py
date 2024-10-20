from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
]

# accounts specific urls
urlpatterns += [path("auth/v1/", include("accounts.urls"))]

# apis specific urls
urlpatterns += [path("apis/v1/", include("apis.urls"))]
