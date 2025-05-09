from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    CategoryViewSet, ItemViewSet,
    ProductionProcessViewSet, PurchaseOrderLineViewSet,
    InventoryTransactionViewSet
)
from apps.inventory.views.recipe_views import RecipeViewSet, RecipeItemViewSet
from apps.inventory.views.production_views import ProductionViewSet
from apps.inventory.views.excel_import_views import (
    ExcelImportListCreateView, ExcelImportDetailView,
    ExcelTemplateView, ExcelTemplateInfoView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')
# BOM endpoint removed in favor of the new Recipe/Production system

# New recipe and production endpoints
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'recipe-items', RecipeItemViewSet, basename='recipe-item')
router.register(r'productions', ProductionViewSet, basename='production')

# Existing endpoints
router.register(r'production-processes', ProductionProcessViewSet, basename='production-process')
router.register(r'purchase-order-lines', PurchaseOrderLineViewSet, basename='purchase-order-line')
router.register(r'inventory-transactions', InventoryTransactionViewSet, basename='inventory-transaction')

urlpatterns = [
    path('', include(router.urls)),
    
    # Excel import endpoints
    path('excel-imports/', ExcelImportListCreateView.as_view(), name='excel-import-list-create'),
    path('excel-imports/<uuid:import_id>/', ExcelImportDetailView.as_view(), name='excel-import-detail'),
    path('excel-templates/<str:import_type>/', ExcelTemplateView.as_view(), name='excel-template'),
    path('excel-templates/', ExcelTemplateInfoView.as_view(), name='excel-template-info'),
]
