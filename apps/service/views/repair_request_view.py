from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.service.models.repair_request import RepairRequest, RepairStatus
from apps.service.serializers.repair_serializer import RepairRequestSerializer, RepairRequestListSerializer
from apps.service.services.repair_request_service import RepairRequestService
from apps.common.responses import success_response, error_response


class RepairRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for repair request operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RepairRequestService()
    
    def list(self, request):
        """
        Get all repair requests.
        """
        repair_requests = self.service.get_all_repair_requests()
        serializer = RepairRequestListSerializer(repair_requests, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get a repair request by ID.
        """
        repair_request = self.service.get_repair_request(pk)
        if not repair_request:
            return error_response(
                error_message=f"Repair request with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = RepairRequestSerializer(repair_request)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new repair request.
        """
        serializer = RepairRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid repair request data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            repair_request = self.service.create_repair_request(serializer.validated_data)
            response_serializer = RepairRequestSerializer(repair_request)
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
        Update an existing repair request.
        """
        existing_request = self.service.get_repair_request(pk)
        if not existing_request:
            return error_response(
                error_message=f"Repair request with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = RepairRequestSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid repair request data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            repair_request = self.service.update_repair_request(pk, serializer.validated_data)
            response_serializer = RepairRequestSerializer(repair_request)
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
        Delete a repair request.
        """
        try:
            result = self.service.delete_repair_request(pk)
            if not result:
                return error_response(
                    error_message=f"Repair request with ID {pk} not found",
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
    def by_device(self, request):
        """
        Get repair requests by device ID.
        """
        device_id = request.query_params.get('device_id', None)
        if not device_id:
            return error_response(
                error_message="device_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        repair_requests = self.service.get_repair_requests_by_device(device_id)
        serializer = RepairRequestListSerializer(repair_requests, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_dealer(self, request):
        """
        Get repair requests by dealer ID.
        """
        dealer_id = request.query_params.get('dealer_id', None)
        if not dealer_id:
            return error_response(
                error_message="dealer_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        repair_requests = self.service.get_repair_requests_by_dealer(dealer_id)
        serializer = RepairRequestListSerializer(repair_requests, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get repair requests by customer ID.
        """
        customer_id = request.query_params.get('customer_id', None)
        if not customer_id:
            return error_response(
                error_message="customer_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        repair_requests = self.service.get_repair_requests_by_customer(customer_id)
        serializer = RepairRequestListSerializer(repair_requests, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get repair requests by status.
        """
        status_param = request.query_params.get('status', None)
        if not status_param:
            return error_response(
                error_message="status query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate status
        status_choices = [choice[0] for choice in RepairStatus.choices]
        if status_param not in status_choices:
            return error_response(
                error_message=f"Invalid status. Must be one of {', '.join(status_choices)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        repair_requests = self.service.get_repair_requests_by_status(status_param)
        serializer = RepairRequestListSerializer(repair_requests, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of a repair request.
        """
        repair_request = self.service.get_repair_request(pk)
        if not repair_request:
            return error_response(
                error_message=f"Repair request with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        status_param = request.data.get('status', None)
        if not status_param:
            return error_response(
                error_message="status field is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate status
        status_choices = [choice[0] for choice in RepairStatus.choices]
        if status_param not in status_choices:
            return error_response(
                error_message=f"Invalid status. Must be one of {', '.join(status_choices)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            repair_request = self.service.update_repair_request_status(pk, status_param)
            serializer = RepairRequestSerializer(repair_request)
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
    def repair_parts(self, request, pk=None):
        """
        Get all repair parts used in a repair request.
        """
        from apps.service.serializers.repair_serializer import RepairPartSerializer
        
        repair_request = self.service.get_repair_request(pk)
        if not repair_request:
            return error_response(
                error_message=f"Repair request with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        repair_parts = self.service.get_repair_parts(pk)
        serializer = RepairPartSerializer(repair_parts, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )