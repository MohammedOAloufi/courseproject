from django.urls import path

from .api import catalog_home_api
from .views import catalog_home

app_name = "catalog"

urlpatterns = [
    # الصفحة الرئيسية (عرض المنتجات)
    path("", catalog_home, name="home"),
    path("api/home/", catalog_home_api, name="home_api"),
]
