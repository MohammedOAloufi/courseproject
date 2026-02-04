from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # لوحة التحكم
    path("admin/", admin.site.urls),

    # الواجهة الرئيسية للعملاء (Home)
    path("", include("catalog.urls")),

    # تطبيقات أخرى
    path("accounts/", include("accounts.urls")),
    path("orders/", include("orders.urls")),
]

# عرض ملفات الميديا أثناء التطوير فقط
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
