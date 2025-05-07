from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.responses import success_response, error_response
from apps.inventory.serializers import InventoryTransactionSerializer
from apps.inventory.models import InventoryTransaction
from apps.inventory.services.inventory_transaction_service import InventoryTransactionService


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for inventory transactions.
    Follows REST principles and uses the service layer for business logic.
    """
    queryset = InventoryTransaction.objects.all().order_by('-transaction_date')
    serializer_class = InventoryTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item', 'transaction_type', 'reference_model', 'reference_id']
    search_fields = ['item__name', 'notes']
    ordering_fields = ['transaction_date', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = InventoryTransactionService()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(success_response(serializer.data))
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Use service layer to handle business logic, including updating item quantity
            transaction = self.service.create_transaction(serializer.validated_data)
            response_serializer = self.get_serializer(transaction)
            return success_response(response_serializer.data, status=201)
        return error_response(serializer.errors, status=400)
    
    def update(self, request, *args, **kwargs):
        # Inventory transactions should not be updated after creation
        # as they represent a historical record of stock movements
        return error_response(
            "Inventory transactions cannot be modified after creation", 
            status=405
        )
        
    def partial_update(self, request, *args, **kwargs):
        # Inventory transactions should not be partially updated after creation
        return error_response(
            "Inventory transactions cannot be modified after creation", 
            status=405
        )
    
    def destroy(self, request, *args, **kwargs):
        # Inventory transactions should not be deleted after creation
        return error_response(
            "Inventory transactions cannot be deleted after creation", 
            status=405
        )
