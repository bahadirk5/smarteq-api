from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    CategoryViewSet, ItemViewSet, BillOfMaterialsViewSet,
    ProductionProcessViewSet, PurchaseOrderLineViewSet,
    InventoryTransactionViewSet
)
from apps.inventory.views.excel_import_views import (
    ExcelImportListCreateView, ExcelImportDetailView,
    ExcelTemplateView, ExcelTemplateInfoView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'boms', BillOfMaterialsViewSet, basename='bill-of-materials')
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
