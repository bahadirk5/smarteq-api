from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    CategoryViewSet, ItemViewSet, BillOfMaterialsViewSet,
    ProductionProcessViewSet, PurchaseOrderLineViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'boms', BillOfMaterialsViewSet, basename='bill-of-materials')
router.register(r'production-processes', ProductionProcessViewSet, basename='production-process')
router.register(r'purchase-order-lines', PurchaseOrderLineViewSet, basename='purchase-order-line')

urlpatterns = [
    path('', include(router.urls)),
]
