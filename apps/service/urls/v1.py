from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.service.views.repair_request_view import RepairRequestViewSet
from apps.service.views.repair_part_view import RepairPartViewSet

# DRF router for viewsets 
router = DefaultRouter()
router.register(r'repair-requests', RepairRequestViewSet, basename='repair-request')
router.register(r'repair-parts', RepairPartViewSet, basename='repair-part')

# URL patterns 
urlpatterns = [
    path('', include(router.urls)),
]