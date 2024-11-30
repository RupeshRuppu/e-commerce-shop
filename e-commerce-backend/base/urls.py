from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def main(req):
    return render(req, "main.html")


urlpatterns = [
    path("", main),
    path("admin/", admin.site.urls),
]

# accounts specific urls
urlpatterns += [path("auth/v1/", include("accounts.urls"))]

# apis specific urls
urlpatterns += [path("apis/v1/", include("apis.urls"))]