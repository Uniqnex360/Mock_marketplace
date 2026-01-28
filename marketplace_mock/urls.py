from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def health_check(request):
    return JsonResponse({"status": "awake", "database": "active"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/amazon-ae/', include('apps.amazon_ae.urls')),
    path('api/noon-ae/', include('apps.noon_ae.urls')),
    path('api/upload/', include('apps.data_upload.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
