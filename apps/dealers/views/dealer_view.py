from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.dealers.models.dealer import Dealer
from apps.dealers.serializers import DealerSerializer, DealerListSerializer
from apps.dealers.services import DealerService
from apps.common.responses import success_response, error_response


class DealerViewSet(viewsets.ViewSet):
    """
    ViewSet for dealer operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DealerService()
    
    def list(self, request):
        """
        Get all dealers.
        """
        dealers = self.service.get_all_dealers()
        serializer = DealerListSerializer(dealers, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get a dealer by ID.
        """
        dealer = self.service.get_dealer(pk)
        if not dealer:
            return error_response(
                error_message=f"Dealer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = DealerSerializer(dealer)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new dealer.
        """
        serializer = DealerSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid dealer data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            dealer = self.service.create_dealer(serializer.validated_data)
            response_serializer = DealerSerializer(dealer)
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
        Update an existing dealer.
        """
        existing_dealer = self.service.get_dealer(pk)
        if not existing_dealer:
            return error_response(
                error_message=f"Dealer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = DealerSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid dealer data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            dealer = self.service.update_dealer(pk, serializer.validated_data)
            response_serializer = DealerSerializer(dealer)
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
        Delete a dealer.
        """
        try:
            result = self.service.delete_dealer(pk)
            if not result:
                return error_response(
                    error_message=f"Dealer with ID {pk} not found",
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
    def active(self, request):
        """
        Get all active dealers.
        """
        dealers = self.service.get_active_dealers()
        serializer = DealerListSerializer(dealers, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['put'])
    def activate(self, request, pk=None):
        """
        Activate a dealer.
        """
        try:
            dealer = self.service.activate_dealer(pk)
            if not dealer:
                return error_response(
                    error_message=f"Dealer with ID {pk} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
                
            serializer = DealerSerializer(dealer)
            return success_response(
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except ValueError as e:
            return error_response(
                error_message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a dealer.
        """
        try:
            dealer = self.service.deactivate_dealer(pk)
            if not dealer:
                return error_response(
                    error_message=f"Dealer with ID {pk} not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
                
            serializer = DealerSerializer(dealer)
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
    def customers(self, request, pk=None):
        """
        Get all customers associated with a dealer.
        """
        from apps.customers.serializers import CustomerListSerializer
        
        dealer = self.service.get_dealer(pk)
        if not dealer:
            return error_response(
                error_message=f"Dealer with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        customers = self.service.get_dealer_customers(pk)
        serializer = CustomerListSerializer(customers, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )