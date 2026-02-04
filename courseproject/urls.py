from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Apps URLs
    path("accounts/", include("accounts.urls")),
    path("catalog/", include("catalog.urls")),
    path("orders/", include("orders.urls")),
]

# Serve media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
