from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("generator.urls")),
    path("api/qr/", include("generator.api_urls")),
]