from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.customers.views.customer_view import CustomerViewSet

# DRF router for viewsets 
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

# URL patterns 
urlpatterns = [
    path('', include(router.urls)),
]