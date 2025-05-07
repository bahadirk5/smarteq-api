from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.common.responses import success_response, error_response
from apps.inventory.services.purchase_history_service import PurchaseHistoryService
from apps.inventory.serializers.purchase_history_serializer import (
    PurchaseHistorySerializer,
    PurchaseHistoryDetailSerializer,
    PurchaseHistoryCreateUpdateSerializer
)


class PurchaseHistoryListCreateView(APIView):
    """
    API endpoint for listing and creating purchase history records
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, item_id):
        """
        Get purchase history for an item
        """
        purchase_history, error = PurchaseHistoryService.get_purchase_history(item_id)
        
        if error:
            return error_response(error, status.HTTP_404_NOT_FOUND)
        
        serializer = PurchaseHistoryDetailSerializer(purchase_history, many=True)
        return success_response(serializer.data)
    
    def post(self, request, item_id):
        """
        Create a new purchase history record
        """
        # Add item_id to request data
        data = request.data.copy()
        data['item_id'] = item_id
        
        serializer = PurchaseHistoryCreateUpdateSerializer(data=data)
        if not serializer.is_valid():
            return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        purchase, error = PurchaseHistoryService.create_purchase_record(
            item_id=item_id,
            purchase_date=serializer.validated_data['purchase_date'],
            quantity=serializer.validated_data['quantity'],
            unit_price=serializer.validated_data['unit_price'],
            supplier=serializer.validated_data.get('supplier'),
            invoice_reference=serializer.validated_data.get('invoice_reference'),
            notes=serializer.validated_data.get('notes')
        )
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        result_serializer = PurchaseHistoryDetailSerializer(purchase)
        return success_response(result_serializer.data, status.HTTP_201_CREATED)


class PurchaseHistoryDetailView(APIView):
    """
    API endpoint for retrieving, updating, and deleting a purchase history record
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, purchase_id):
        """
        Get a purchase history record by ID
        """
        purchase = PurchaseHistoryService.get_by_id(purchase_id)
        if not purchase:
            return error_response('Purchase history not found', status.HTTP_404_NOT_FOUND)
        
        serializer = PurchaseHistoryDetailSerializer(purchase)
        return success_response(serializer.data)
    
    def put(self, request, purchase_id):
        """
        Update a purchase history record
        """
        serializer = PurchaseHistoryCreateUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        purchase, error = PurchaseHistoryService.update_purchase_record(
            purchase_id=purchase_id,
            **serializer.validated_data
        )
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        result_serializer = PurchaseHistoryDetailSerializer(purchase)
        return success_response(result_serializer.data)
    
    def delete(self, request, purchase_id):
        """
        Delete a purchase history record
        """
        result, error = PurchaseHistoryService.delete_purchase_record(purchase_id)
        
        if error:
            return error_response(error, status.HTTP_400_BAD_REQUEST)
        
        return success_response({'message': 'Purchase history record deleted successfully'})
