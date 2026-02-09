from django.urls import path
from .views import catalog_home

app_name = "catalog"

urlpatterns = [
    # الصفحة الرئيسية (عرض المنتجات)
    path("", catalog_home, name="home"),
]
