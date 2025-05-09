from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dealers.views.dealer_view import DealerViewSet

# DRF router for viewsets 
router = DefaultRouter()
router.register(r'dealers', DealerViewSet, basename='dealer')

# URL patterns 
urlpatterns = [
    path('', include(router.urls)),
]