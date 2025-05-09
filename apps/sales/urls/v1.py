from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.sales.views.order_view import OrderViewSet
from apps.sales.views.order_item_view import OrderItemViewSet
from apps.sales.views.device_view import DeviceViewSet

# DRF router for viewsets 
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'devices', DeviceViewSet, basename='device')

# URL patterns 
urlpatterns = [
    path('', include(router.urls)),
]