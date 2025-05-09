from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.customers.models.customer import Customer
from apps.customers.serializers import CustomerSerializer, CustomerListSerializer
from apps.customers.services import CustomerService
from apps.common.responses import success_response, error_response


class CustomerViewSet(viewsets.ViewSet):
    """
    ViewSet for customer operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerService()
    
    def list(self, request):
        """
        Get all customers.
        """
        customers = self.service.get_all_customers()
        serializer = CustomerListSerializer(customers, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get a customer by ID.
        """
        customer = self.service.get_customer(pk)
        if not customer:
            return error_response(
                error_message=f"Customer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = CustomerSerializer(customer)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new customer.
        """
        serializer = CustomerSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid customer data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            customer = self.service.create_customer(serializer.validated_data)
            response_serializer = CustomerSerializer(customer)
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
        Update an existing customer.
        """
        existing_customer = self.service.get_customer(pk)
        if not existing_customer:
            return error_response(
                error_message=f"Customer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = CustomerSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid customer data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            customer = self.service.update_customer(pk, serializer.validated_data)
            response_serializer = CustomerSerializer(customer)
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
        Delete a customer.
        """
        try:
            result = self.service.delete_customer(pk)
            if not result:
                return error_response(
                    error_message=f"Customer with ID {pk} not found",
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
    def by_dealer(self, request):
        """
        Get customers by dealer ID.
        """
        dealer_id = request.query_params.get('dealer_id', None)
        if not dealer_id:
            return error_response(
                error_message="dealer_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        customers = self.service.get_customers_by_dealer(dealer_id)
        serializer = CustomerListSerializer(customers, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get customers by customer type.
        """
        customer_type = request.query_params.get('type', None)
        if not customer_type:
            return error_response(
                error_message="type query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        customers = self.service.get_customers_by_type(customer_type)
        serializer = CustomerListSerializer(customers, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def devices(self, request, pk=None):
        """
        Get all devices owned by a customer.
        """
        from apps.sales.serializers import DeviceListSerializer
        
        customer = self.service.get_customer(pk)
        if not customer:
            return error_response(
                error_message=f"Customer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        devices = self.service.get_customer_devices(pk)
        serializer = DeviceListSerializer(devices, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """
        Get all orders placed by a customer.
        """
        from apps.sales.serializers import OrderListSerializer
        
        customer = self.service.get_customer(pk)
        if not customer:
            return error_response(
                error_message=f"Customer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        orders = self.service.get_customer_orders(pk)
        serializer = OrderListSerializer(orders, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )