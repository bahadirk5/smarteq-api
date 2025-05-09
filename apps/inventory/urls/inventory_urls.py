from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    CategoryViewSet, ItemViewSet, RecipeViewSet, RecipeItemViewSet,
    ProductionViewSet, ProductionProcessViewSet, PurchaseOrderLineViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')
# BOM endpoint replaced with Recipe and Production endpoints
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'recipe-items', RecipeItemViewSet, basename='recipe-item')
router.register(r'productions', ProductionViewSet, basename='production')
router.register(r'production-processes', ProductionProcessViewSet, basename='production-process')
router.register(r'purchase-order-lines', PurchaseOrderLineViewSet, basename='purchase-order-line')

urlpatterns = [
    path('', include(router.urls)),
]
