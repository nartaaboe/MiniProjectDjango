from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from debug_toolbar.toolbar import debug_toolbar_urls

# Admin URL
admin_urlpatterns = [
    path('admin/', admin.site.urls),
]

# API URL patterns
api_urlpatterns = [
    path('api/', include("apps.users.urls")),
    path('api/', include("apps.products.urls")),
    path('api/', include("apps.trading.urls")),
    path('api/', include("apps.sales.urls")),
]

# Schema URL patterns
schema_urlpatterns = [
    path('api/schema/download/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Debug toolbar URL patterns
debug_toolbar_urlpatterns = debug_toolbar_urls()

# Prometheus URL patterns
prometheus_urlpatterns = [ path('', include('django_prometheus.urls')), ]

# Static files URL patterns
static_urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Combine all URL patterns
urlpatterns = (
    admin_urlpatterns +
    api_urlpatterns +
    schema_urlpatterns +
    debug_toolbar_urlpatterns +
    prometheus_urlpatterns +
    static_urlpatterns
)