from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.service.models.repair_part import RepairPart
from apps.service.serializers.repair_serializer import RepairPartSerializer, RepairPartListSerializer
from apps.service.services.repair_part_service import RepairPartService
from apps.common.responses import success_response, error_response


class RepairPartViewSet(viewsets.ViewSet):
    """
    ViewSet for repair part operations.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RepairPartService()
    
    def list(self, request):
        """
        Get all repair parts.
        """
        repair_parts = self.service.get_all_repair_parts()
        serializer = RepairPartListSerializer(repair_parts, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, pk=None):
        """
        Get a repair part by ID.
        """
        repair_part = self.service.get_repair_part(pk)
        if not repair_part:
            return error_response(
                error_message=f"Repair part with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = RepairPartSerializer(repair_part)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def create(self, request):
        """
        Create a new repair part.
        """
        serializer = RepairPartSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid repair part data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            repair_part = self.service.create_repair_part(serializer.validated_data)
            response_serializer = RepairPartSerializer(repair_part)
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
        Update an existing repair part.
        """
        existing_part = self.service.get_repair_part(pk)
        if not existing_part:
            return error_response(
                error_message=f"Repair part with ID {pk} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        serializer = RepairPartSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                error_message="Invalid repair part data",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            repair_part = self.service.update_repair_part(pk, serializer.validated_data)
            response_serializer = RepairPartSerializer(repair_part)
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
        Delete a repair part.
        """
        try:
            result = self.service.delete_repair_part(pk)
            if not result:
                return error_response(
                    error_message=f"Repair part with ID {pk} not found",
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
    def by_repair_request(self, request):
        """
        Get repair parts by repair request ID.
        """
        repair_request_id = request.query_params.get('repair_request_id', None)
        if not repair_request_id:
            return error_response(
                error_message="repair_request_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        repair_parts = self.service.get_repair_parts_by_request(repair_request_id)
        serializer = RepairPartListSerializer(repair_parts, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_item(self, request):
        """
        Get repair parts by inventory item ID.
        """
        item_id = request.query_params.get('item_id', None)
        if not item_id:
            return error_response(
                error_message="item_id query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        repair_parts = self.service.get_repair_parts_by_item(item_id)
        serializer = RepairPartListSerializer(repair_parts, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def warranty_covered(self, request):
        """
        Get repair parts that are covered by warranty.
        """
        repair_parts = self.service.get_warranty_covered_parts()
        serializer = RepairPartListSerializer(repair_parts, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def non_warranty(self, request):
        """
        Get repair parts that are not covered by warranty.
        """
        repair_parts = self.service.get_non_warranty_parts()
        serializer = RepairPartListSerializer(repair_parts, many=True)
        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )