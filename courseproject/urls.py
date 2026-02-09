from django.contrib import admin
from django.urls import path, include
from django.conf import settings      # ✅ هذا السطر كان ناقص
from django.conf.urls.static import static

from catalog.views import catalog_home

urlpatterns = [
    # لوحة التحكم
    path("admin/", admin.site.urls),

    # 🏠 الصفحة الرئيسية الأساسية
    path("", catalog_home, name="home"),

    # التطبيقات
    path("accounts/", include("accounts.urls")),
    path("catalog/", include("catalog.urls")),
    path("orders/", include("orders.urls")),
]

# عرض ملفات الميديا أثناء التطوير فقط
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
