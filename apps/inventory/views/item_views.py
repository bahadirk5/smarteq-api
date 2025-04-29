from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.inventory.serializers import (
    ItemSerializer, ItemListSerializer, ItemDetailSerializer, ItemCreateUpdateSerializer
)
from apps.inventory.services import ItemService
from apps.common.responses import success_response, error_response


class ItemViewSet(viewsets.ViewSet):
    """API endpoints for managing inventory items."""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ItemService()
    
    def list(self, request):
        """Get all items"""
        items = self.service.get_all_items()
        serializer = ItemListSerializer(items, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get a specific item by ID"""
        try:
            item = self.service.get_item(pk)
            serializer = ItemDetailSerializer(item)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    def create(self, request):
        """Create a new item"""
        serializer = ItemCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                item = self.service.create_item(serializer.validated_data)
                result_serializer = ItemDetailSerializer(item)
                return success_response(
                    data=result_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def update(self, request, pk=None):
        """Update an existing item"""
        serializer = ItemCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                item = self.service.update_item(pk, serializer.validated_data)
                result_serializer = ItemDetailSerializer(item)
                return success_response(data=result_serializer.data)
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def partial_update(self, request, pk=None):
        """Partially update an existing item"""
        try:
            item = self.service.get_item(pk)
            serializer = ItemCreateUpdateSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                updated_item = self.service.update_item(pk, serializer.validated_data)
                result_serializer = ItemDetailSerializer(updated_item)
                return success_response(data=result_serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
    def destroy(self, request, pk=None):
        """Delete an item"""
        try:
            self.service.delete_item(pk)
            return success_response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_sku(self, request):
        """Get an item by its SKU"""
        sku = request.query_params.get('sku')
        if not sku:
            return error_response('SKU parameter is required')
            
        try:
            item = self.service.get_item_by_sku(sku)
            serializer = ItemDetailSerializer(item)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get all items in a specific category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return error_response('category_id parameter is required')
            
        try:
            items = self.service.get_items_by_category(category_id)
            serializer = ItemListSerializer(items, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get all items of a specific type"""
        item_type = request.query_params.get('type')
        if not item_type:
            return error_response('type parameter is required')
            
        try:
            items = self.service.get_items_by_type(item_type)
            serializer = ItemListSerializer(items, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
            
    @action(detail=False, methods=['get'])
    def raw_materials(self, request):
        """Get all raw materials"""
        try:
            items = self.service.get_raw_materials()
            serializer = ItemListSerializer(items, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
            
    @action(detail=False, methods=['get'])
    def intermediate_products(self, request):
        """Get all intermediate products"""
        try:
            items = self.service.get_intermediate_products()
            serializer = ItemListSerializer(items, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
            
    @action(detail=False, methods=['get'])
    def final_products(self, request):
        """Get all final products"""
        try:
            items = self.service.get_final_products()
            serializer = ItemListSerializer(items, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
