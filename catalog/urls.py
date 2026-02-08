from django.urls import path
from .views import catalog_home

app_name = "catalog"

urlpatterns = [
    path("", catalog_home, name="catalog_home"),
]
