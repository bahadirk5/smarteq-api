from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.inventory.serializers import (
    CategorySerializer, CategoryListSerializer, 
    CategoryDetailSerializer, CategoryHierarchySerializer
)
from apps.inventory.services import CategoryService
from apps.common.responses import success_response, error_response


class CategoryViewSet(viewsets.ViewSet):
    """API endpoints for managing inventory categories."""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CategoryService()
    
    def list(self, request):
        """Get all categories"""
        categories = self.service.get_all_categories()
        serializer = CategoryListSerializer(categories, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get a specific category by ID"""
        try:
            category = self.service.get_category(pk)
            serializer = CategoryDetailSerializer(category)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    def create(self, request):
        """Create a new category"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                validated_data = serializer.validated_data.copy()
                # parent_category alanını düzgün formata getir
                if 'parent_category' in validated_data and isinstance(validated_data['parent_category'], dict):
                    if 'id' in validated_data['parent_category']:
                        validated_data['parent_category_id'] = validated_data['parent_category']['id']
                    del validated_data['parent_category']
                
                category = self.service.create_category(validated_data)
                result_serializer = CategoryDetailSerializer(category)
                data = result_serializer.data
                data['message'] = "Kategori başarıyla oluşturuldu"
                return success_response(
                    data=data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def update(self, request, pk=None):
        """Update an existing category"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                validated_data = serializer.validated_data.copy()
                
                # parent_category alanını düzgün formata getir
                if 'parent_category' in validated_data and isinstance(validated_data['parent_category'], dict):
                    if 'id' in validated_data['parent_category']:
                        validated_data['parent_category_id'] = validated_data['parent_category']['id']
                    del validated_data['parent_category']
                
                category = self.service.update_category(pk, validated_data)
                result_serializer = CategoryDetailSerializer(category)
                data = result_serializer.data
                data['message'] = "Kategori başarıyla güncellendi"
                return success_response(
                    data=data,
                    status_code=status.HTTP_200_OK
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def partial_update(self, request, pk=None):
        """Partially update an existing category"""
        try:
            category = self.service.get_category(pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data.copy()
                
                # parent_category alanını düzgün formata getir
                if 'parent_category' in validated_data and isinstance(validated_data['parent_category'], dict):
                    if 'id' in validated_data['parent_category']:
                        validated_data['parent_category_id'] = validated_data['parent_category']['id']
                    del validated_data['parent_category']
                
                updated_category = self.service.update_category(pk, validated_data)
                result_serializer = CategoryDetailSerializer(updated_category)
                data = result_serializer.data
                data['message'] = "Kategori başarıyla güncellendi"
                return success_response(
                    data=data,
                    status_code=status.HTTP_200_OK
                )
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
    def destroy(self, request, pk=None):
        """Delete a category"""
        try:
            category = self.service.get_category(pk)
            category_id = category.id
            category_name = category.name
            self.service.delete_category(pk)
            return success_response(
                data={
                    "id": str(category_id), 
                    "name": category_name,
                    "message": "Kategori başarıyla silindi"
                },
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get hierarchical structure of categories"""
        try:
            # Get all root categories
            root_categories = self.service.get_root_categories()
            # Use the serializer directly on the ORM objects
            serializer = CategoryHierarchySerializer(root_categories, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def root(self, request):
        """Get all root categories (without parent)"""
        try:
            categories = self.service.get_root_categories()
            serializer = CategoryListSerializer(categories, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
