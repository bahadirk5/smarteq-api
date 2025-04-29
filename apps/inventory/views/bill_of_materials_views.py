from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.inventory.serializers import (
    BillOfMaterialsSerializer, BillOfMaterialsDetailSerializer,
    BOMComponentSerializer, BOMComponentCreateSerializer, BOMHierarchySerializer
)
from apps.inventory.services import BillOfMaterialsService
from apps.common.responses import success_response, error_response


class BillOfMaterialsViewSet(viewsets.ViewSet):
    """API endpoints for managing Bills of Materials."""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = BillOfMaterialsService()
    
    def list(self, request):
        """Get all bills of materials"""
        boms = self.service.get_all_boms()
        serializer = BillOfMaterialsDetailSerializer(boms, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get a specific bill of materials by ID"""
        try:
            bom = self.service.get_bom(pk)
            serializer = BillOfMaterialsDetailSerializer(bom)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    def create(self, request):
        """Create a new bill of materials entry"""
        serializer = BillOfMaterialsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                bom = self.service.create_bom(serializer.validated_data)
                result_serializer = BillOfMaterialsDetailSerializer(bom)
                return success_response(
                    data=result_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def update(self, request, pk=None):
        """Update an existing bill of materials entry"""
        serializer = BillOfMaterialsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                bom = self.service.update_bom(pk, serializer.validated_data)
                result_serializer = BillOfMaterialsDetailSerializer(bom)
                return success_response(data=result_serializer.data)
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def partial_update(self, request, pk=None):
        """Partially update an existing bill of materials entry"""
        try:
            bom = self.service.get_bom(pk)
            serializer = BillOfMaterialsSerializer(bom, data=request.data, partial=True)
            if serializer.is_valid():
                updated_bom = self.service.update_bom(pk, serializer.validated_data)
                result_serializer = BillOfMaterialsDetailSerializer(updated_bom)
                return success_response(data=result_serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
    def destroy(self, request, pk=None):
        """Delete a bill of materials entry"""
        try:
            self.service.delete_bom(pk)
            return success_response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_output_item(self, request):
        """Get all components for a specific output item"""
        item_id = request.query_params.get('item_id')
        if not item_id:
            return error_response('item_id parameter is required')
            
        try:
            boms = self.service.get_bom_for_item(item_id)
            serializer = BOMComponentSerializer(boms, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def recursive(self, request):
        """Get a recursive bill of materials for an item"""
        item_id = request.query_params.get('item_id')
        if not item_id:
            return error_response('item_id parameter is required')
            
        try:
            recursive_bom = self.service.get_recursive_bom(item_id)
            serializer = BOMHierarchySerializer(recursive_bom)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['post'])
    def create_complete_bom(self, request):
        """Create a complete bill of materials with multiple components"""
        output_item_id = request.data.get('output_item_id')
        components_data = request.data.get('components', [])
        
        if not output_item_id:
            return error_response('output_item_id is required')
            
        if not components_data:
            return error_response('At least one component is required')
        
        components_serializer = BOMComponentCreateSerializer(data=components_data, many=True)
        if not components_serializer.is_valid():
            return error_response(components_serializer.errors)
            
        try:
            boms = self.service.create_complete_bom(output_item_id, components_serializer.validated_data)
            result_serializer = BOMComponentSerializer(boms, many=True)
            return success_response(
                data=result_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(str(e))
