"""
URL Configuration for smarteq project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Smarteq API",
      default_version='v1',
      description="API documentation for Smarteq",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=False,
   permission_classes=(IsAuthenticated,),
)

API_VERSION = 'v1'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path(f'api/{API_VERSION}/', include([
        # Include app URLs here
        path('users/', include('apps.users.urls.v1')),
        path('projects/', include('apps.projects.urls.v1')),
        path('inventory/', include('apps.inventory.urls.v1')),
        path('customers/', include('apps.customers.urls.v1')),
        path('dealers/', include('apps.dealers.urls.v1')),
        path('sales/', include('apps.sales.urls.v1')),
        path('service/', include('apps.service.urls.v1')),
    ])),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', lambda request: redirect('schema-swagger-ui'), name='root-redirect'),
]

# Add debug_toolbar URLs in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
        
        # Serve media files in development
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    except ImportError:
        pass