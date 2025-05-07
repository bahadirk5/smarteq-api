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
        # Debug için Request data'yu loglayalım
        print("Request data:", request.data)
        
        serializer = ItemCreateUpdateSerializer(data=request.data)
        print("Is Valid:", serializer.is_valid())
        
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return error_response(serializer.errors)
        
        try:
            # Debug için validated_data'yu loglayalım
            print("Validated data:", serializer.validated_data)
            
            # Proje ID'sini request.data'dan al
            project_id = request.data.get('project_id')
            print("Project ID:", project_id)
            
            quantity = request.data.get('quantity', 0)
            minimum_stock_level = request.data.get('minimum_stock_level', 0)
            notes = request.data.get('notes')
            
            # Eğer proje ID varsa, ürünü projeye atayarak oluştur
            if project_id:
                try:
                    item = self.service.create_item_with_project(
                        serializer.validated_data, 
                        project_id=project_id,
                        quantity=quantity,
                        minimum_stock_level=minimum_stock_level,
                        notes=notes
                    )
                except Exception as e:
                    print("Error in create_item_with_project:", str(e))
                    return error_response(str(e))
            else:
                # Normal ürün oluştur işlemi
                item = self.service.create_item(serializer.validated_data)
                
            result_serializer = ItemDetailSerializer(item)
            return success_response(
                data=result_serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            print("Exception in create:", str(e))
            return error_response(str(e))
    
    def update(self, request, pk=None):
        """Update an existing item"""
        try:
            # Önce mevcut ürünü al
            instance = self.service.get_item(pk)
            # instance parametresini ekleyerek serializer oluştur
            serializer = ItemCreateUpdateSerializer(instance, data=request.data)
            if serializer.is_valid():
                try:
                    item = self.service.update_item(pk, serializer.validated_data)
                    result_serializer = ItemDetailSerializer(item)
                    return success_response(data=result_serializer.data)
                except Exception as e:
                    return error_response(str(e))
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
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
            item = self.service.get_item(pk)
            item_id = item.id
            item_name = item.name
            item_sku = item.sku
            self.service.delete_item(pk)
            return success_response(
                data={
                    "id": str(item_id), 
                    "name": item_name, 
                    "sku": item_sku,
                    "message": "Ürün başarıyla silindi"
                },
                status_code=status.HTTP_200_OK
            )
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
    
    @action(detail=True, methods=['get'])
    def get_quantity(self, request, pk=None):
        """Get the current quantity of an item"""
        try:
            quantity = self.service.get_item_quantity(pk)
            return success_response(data={'quantity': quantity})
        except Exception as e:
            return error_response(str(e))
            
    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        """Update the quantity of an item"""
        try:
            quantity = request.data.get('quantity')
            if quantity is None:
                return error_response('quantity parameter is required')
                
            try:
                quantity = int(quantity)
            except ValueError:
                return error_response('quantity must be an integer')
                
            item = self.service.update_item_quantity(pk, quantity)
            serializer = ItemDetailSerializer(item)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
