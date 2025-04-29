from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.inventory.serializers import (
    PurchaseOrderLineSerializer, PurchaseOrderLineDetailSerializer,
    PurchaseOrderLineBulkCreateSerializer, PurchaseOrderSummarySerializer
)
from apps.inventory.services import PurchaseOrderLineService
from apps.common.responses import success_response, error_response


class PurchaseOrderLineViewSet(viewsets.ViewSet):
    """API endpoints for managing Purchase Order Lines."""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PurchaseOrderLineService()
    
    def list(self, request):
        """Get all purchase order lines"""
        lines = self.service.get_all_purchase_order_lines()
        serializer = PurchaseOrderLineDetailSerializer(lines, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get a specific purchase order line by ID"""
        try:
            line = self.service.get_purchase_order_line(pk)
            serializer = PurchaseOrderLineDetailSerializer(line)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    def create(self, request):
        """Create a new purchase order line"""
        serializer = PurchaseOrderLineSerializer(data=request.data)
        if serializer.is_valid():
            try:
                line = self.service.create_purchase_order_line(serializer.validated_data)
                result_serializer = PurchaseOrderLineDetailSerializer(line)
                return success_response(
                    data=result_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def update(self, request, pk=None):
        """Update an existing purchase order line"""
        serializer = PurchaseOrderLineSerializer(data=request.data)
        if serializer.is_valid():
            try:
                line = self.service.update_purchase_order_line(pk, serializer.validated_data)
                result_serializer = PurchaseOrderLineDetailSerializer(line)
                return success_response(data=result_serializer.data)
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def partial_update(self, request, pk=None):
        """Partially update an existing purchase order line"""
        try:
            line = self.service.get_purchase_order_line(pk)
            serializer = PurchaseOrderLineSerializer(line, data=request.data, partial=True)
            if serializer.is_valid():
                updated_line = self.service.update_purchase_order_line(pk, serializer.validated_data)
                result_serializer = PurchaseOrderLineDetailSerializer(updated_line)
                return success_response(data=result_serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
    def destroy(self, request, pk=None):
        """Delete a purchase order line"""
        try:
            self.service.delete_purchase_order_line(pk)
            return success_response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_purchase_order(self, request):
        """Get all lines for a specific purchase order"""
        purchase_order_id = request.query_params.get('purchase_order_id')
        if not purchase_order_id:
            return error_response('purchase_order_id parameter is required')
            
        try:
            purchase_order_summary = self.service.get_lines_by_purchase_order(purchase_order_id)
            serializer = PurchaseOrderSummarySerializer(purchase_order_summary)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_item(self, request):
        """Get purchase history for a specific item"""
        item_id = request.query_params.get('item_id')
        if not item_id:
            return error_response('item_id parameter is required')
            
        try:
            purchase_lines = self.service.get_purchased_items_history(item_id)
            serializer = PurchaseOrderLineDetailSerializer(purchase_lines, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['post'])
    def create_multiple(self, request):
        """Create multiple purchase order lines for a purchase order"""
        purchase_order_id = request.data.get('purchase_order_id')
        lines_data = request.data.get('lines', [])
        
        if not purchase_order_id:
            return error_response('purchase_order_id is required')
            
        if not lines_data:
            return error_response('At least one line is required')
        
        lines_serializer = PurchaseOrderLineBulkCreateSerializer(data=lines_data, many=True)
        if not lines_serializer.is_valid():
            return error_response(lines_serializer.errors)
            
        try:
            lines = self.service.create_multiple_lines(purchase_order_id, lines_serializer.validated_data)
            result_serializer = PurchaseOrderLineDetailSerializer(lines, many=True)
            return success_response(
                data=result_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(str(e))
