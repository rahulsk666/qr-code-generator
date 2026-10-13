from django.urls import path
from . import api_views

urlpatterns = [
    path("generate/", api_views.generate_qr_api, name="api-generate"),
    path("history/", api_views.qr_history_api, name="api-history"),
]