from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.sales.models.device import Device
from apps.sales.serializers import DeviceSerializer, DeviceListSerializer
from apps.sales.services import DeviceService
from apps.common.responses import success_response, error_response


class DeviceViewSet(viewsets.ViewSet):
    """
    ViewSet for device operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DeviceService()
    
    def list(self, request):
        """
        Get all devices.
        """
        devices = self.service.get_all_devices()
        serializer = DeviceListSerializer(devices, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get a device by ID.
        """
        device = self.service.get_device(pk)
        if not device:
            return error_response(
                error_message=f"Device with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = DeviceSerializer(device)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new device.
        """
        serializer = DeviceSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid device data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            device = self.service.create_device(serializer.validated_data)
            response_serializer = DeviceSerializer(device)
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
        Update an existing device.
        """
        existing_device = self.service.get_device(pk)
        if not existing_device:
            return error_response(
                error_message=f"Device with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = DeviceSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid device data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            device = self.service.update_device(pk, serializer.validated_data)
            response_serializer = DeviceSerializer(device)
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
        Delete a device.
        """
        try:
            result = self.service.delete_device(pk)
            if not result:
                return error_response(
                    error_message=f"Device with ID {pk} not found",
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
        Get devices by customer ID.
        """
        customer_id = request.query_params.get('customer_id', None)
        if not customer_id:
            return error_response(
                error_message="customer_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        devices = self.service.get_devices_by_customer(customer_id)
        serializer = DeviceListSerializer(devices, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_serial(self, request):
        """
        Get device by serial number.
        """
        serial_number = request.query_params.get('serial_number', None)
        if not serial_number:
            return error_response(
                error_message="serial_number query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        device = self.service.get_device_by_serial_number(serial_number)
        if not device:
            return error_response(
                error_message=f"Device with serial number {serial_number} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = DeviceSerializer(device)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def warranty_status(self, request, pk=None):
        """
        Get warranty status of a device.
        """
        device = self.service.get_device(pk)
        if not device:
            return error_response(
                error_message=f"Device with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        warranty_info = self.service.get_warranty_status(pk)
        return success_response(
            data=warranty_info,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def repair_history(self, request, pk=None):
        """
        Get repair history of a device.
        """
        from apps.service.serializers import RepairRequestListSerializer
        
        device = self.service.get_device(pk)
        if not device:
            return error_response(
                error_message=f"Device with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        repairs = self.service.get_repair_history(pk)
        serializer = RepairRequestListSerializer(repairs, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )