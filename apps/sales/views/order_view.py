from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.sales.models.order import Order, OrderStatus
from apps.sales.serializers import OrderSerializer, OrderListSerializer
from apps.sales.services import OrderService
from apps.common.responses import success_response, error_response


class OrderViewSet(viewsets.ViewSet):
    """
    ViewSet for order operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OrderService()
    
    def list(self, request):
        """
        Get all orders.
        """
        orders = self.service.get_all_orders()
        serializer = OrderListSerializer(orders, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get an order by ID.
        """
        order = self.service.get_order(pk)
        if not order:
            return error_response(
                error_message=f"Order with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = OrderSerializer(order)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new order.
        """
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid order data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            order = self.service.create_order(serializer.validated_data)
            response_serializer = OrderSerializer(order)
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
        Update an existing order.
        """
        existing_order = self.service.get_order(pk)
        if not existing_order:
            return error_response(
                error_message=f"Order with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = OrderSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid order data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            order = self.service.update_order(pk, serializer.validated_data)
            response_serializer = OrderSerializer(order)
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
        Delete an order.
        """
        try:
            result = self.service.delete_order(pk)
            if not result:
                return error_response(
                    error_message=f"Order with ID {pk} not found",
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
    def by_customer(self, request):
        """
        Get orders by customer ID.
        """
        customer_id = request.query_params.get('customer_id', None)
        if not customer_id:
            return error_response(
                error_message="customer_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        orders = self.service.get_orders_by_customer(customer_id)
        serializer = OrderListSerializer(orders, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get orders by status.
        """
        status_param = request.query_params.get('status', None)
        if not status_param:
            return error_response(
                error_message="status query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate status
        status_choices = [choice[0] for choice in OrderStatus.choices]
        if status_param not in status_choices:
            return error_response(
                error_message=f"Invalid status. Must be one of {', '.join(status_choices)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        orders = self.service.get_orders_by_status(status_param)
        serializer = OrderListSerializer(orders, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of an order.
        """
        order = self.service.get_order(pk)
        if not order:
            return error_response(
                error_message=f"Order with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        status_param = request.data.get('status', None)
        if not status_param:
            return error_response(
                error_message="status field is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate status
        status_choices = [choice[0] for choice in OrderStatus.choices]
        if status_param not in status_choices:
            return error_response(
                error_message=f"Invalid status. Must be one of {', '.join(status_choices)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            updated_order = self.service.update_order_status(pk, status_param)
            serializer = OrderSerializer(updated_order)
            return success_response(
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                error_message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def generate_invoice(self, request, pk=None):
        """
        Generate an invoice for an order.
        """
        order = self.service.get_order(pk)
        if not order:
            return error_response(
                error_message=f"Order with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        try:
            invoice_data = self.service.generate_invoice(pk)
            return success_response(
                data=invoice_data,
                status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                error_message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )