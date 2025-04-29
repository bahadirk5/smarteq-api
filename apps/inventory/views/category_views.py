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
                category = self.service.create_category(serializer.validated_data)
                result_serializer = CategoryDetailSerializer(category)
                return success_response(
                    data=result_serializer.data,
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
                category = self.service.update_category(pk, serializer.validated_data)
                result_serializer = CategoryDetailSerializer(category)
                return success_response(data=result_serializer.data)
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def partial_update(self, request, pk=None):
        """Partially update an existing category"""
        try:
            category = self.service.get_category(pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                updated_category = self.service.update_category(pk, serializer.validated_data)
                result_serializer = CategoryDetailSerializer(updated_category)
                return success_response(data=result_serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
    def destroy(self, request, pk=None):
        """Delete a category"""
        try:
            self.service.delete_category(pk)
            return success_response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get hierarchical structure of categories"""
        try:
            hierarchy = self.service.get_category_hierarchy()
            serializer = CategoryHierarchySerializer(hierarchy, many=True)
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
