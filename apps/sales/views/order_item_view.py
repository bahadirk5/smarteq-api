from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.sales.models.order import OrderItem
from apps.sales.serializers import OrderItemSerializer, OrderItemListSerializer
from apps.sales.services import OrderItemService
from apps.common.responses import success_response, error_response


class OrderItemViewSet(viewsets.ViewSet):
    """
    ViewSet for order item operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderItemService()
    
    def list(self, request):
        """
        Get all order items.
        """
        order_items = self.service.get_all_order_items()
        serializer = OrderItemListSerializer(order_items, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get an order item by ID.
        """
        order_item = self.service.get_order_item(pk)
        if not order_item:
            return error_response(
                error_message=f"Order item with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = OrderItemSerializer(order_item)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new order item.
        """
        serializer = OrderItemSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid order item data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            order_item = self.service.create_order_item(serializer.validated_data)
            response_serializer = OrderItemSerializer(order_item)
            return success_response(
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return error_response(
                error_message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @transaction.atomic
    def update(self, request, pk=None):
        """
        Update an existing order item.
        """
        existing_item = self.service.get_order_item(pk)
        if not existing_item:
            return error_response(
                error_message=f"Order item with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = OrderItemSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid order item data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            order_item = self.service.update_order_item(pk, serializer.validated_data)
            response_serializer = OrderItemSerializer(order_item)
            return success_response(
                data=response_serializer.data,
                status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                error_message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @transaction.atomic
    def destroy(self, request, pk=None):
        """
        Delete an order item.
        """
        try:
            result = self.service.delete_order_item(pk)
            if not result:
                return error_response(
                    error_message=f"Order item with ID {pk} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
                
            return success_response(
                data=None,
                status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                error_message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        """
        Get order items by order ID.
        """
        order_id = request.query_params.get('order_id', None)
        if not order_id:
            return error_response(
                error_message="order_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        order_items = self.service.get_order_items_by_order(order_id)
        serializer = OrderItemListSerializer(order_items, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Get order items by product ID.
        """
        product_id = request.query_params.get('product_id', None)
        if not product_id:
            return error_response(
                error_message="product_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        order_items = self.service.get_order_items_by_product(product_id)
        serializer = OrderItemListSerializer(order_items, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )