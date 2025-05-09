from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.inventory.models.recipe import Recipe
from apps.inventory.models.recipe_item import RecipeItem
from apps.inventory.serializers.recipe_serializers import (
    RecipeSerializer, RecipeDetailSerializer, RecipeCreateUpdateSerializer,
    RecipeItemSerializer, RecipeItemCreateUpdateSerializer
)
from apps.inventory.services.recipe_service import RecipeService


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for Recipe operations"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_fields = ['name', 'output_item_id', 'active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer
    
    def get_service(self):
        return RecipeService()
    
    def list(self, request, *args, **kwargs):
        try:
            # Extract query parameters
            filters = {}
            if 'name' in request.query_params:
                filters['name'] = request.query_params.get('name')
            if 'output_item_id' in request.query_params:
                filters['output_item_id'] = request.query_params.get('output_item_id')
            if 'active' in request.query_params:
                filters['active'] = request.query_params.get('active').lower() == 'true'
            
            # Use service to get recipes
            service_response = self.get_service().get_all_recipes(filters)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                serializer = self.get_serializer(response_data.get('data'), many=True)
                return Response({
                    'data': serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            return service_response
        except Exception as e:
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            recipe_id = kwargs.get('pk')
            service_response = self.get_service().get_recipe_by_id(recipe_id)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                serializer = self.get_serializer(response_data.get('data'))
                return Response({
                    'data': serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            return service_response
        except Exception as e:
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Extract recipe items if provided
            recipe_items_data = request.data.get('items', [])
            
            service_response = self.get_service().create_recipe(serializer.validated_data, recipe_items_data)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                result_serializer = RecipeDetailSerializer(response_data.get('data'))
                return Response({
                    'data': result_serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            return service_response
        except Exception as e:
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        try:
            recipe_id = kwargs.get('pk')
            
            # Partial update for PATCH
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            service_response = self.get_service().update_recipe(recipe_id, serializer.validated_data)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                result_serializer = RecipeDetailSerializer(response_data.get('data'))
                return Response({
                    'data': result_serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            return service_response
        except Exception as e:
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        try:
            recipe_id = kwargs.get('pk')
            service_response = self.get_service().delete_recipe(recipe_id)
            
            # Just return the ApiResponse directly for delete operations
            return service_response
        except Exception as e:
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='items')
    def recipe_items(self, request, pk=None):
        """Get all items for a specific recipe"""
        try:
            response = self.get_service().get_recipe_items(pk)
            
            if response.get('success', False):
                serializer = RecipeItemSerializer(response.get('data'), many=True)
                return Response({'success': True, 'data': serializer.data})
            
            return Response(response, status=response.get('status_code', status.HTTP_400_BAD_REQUEST))
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='items')
    def add_recipe_item(self, request, pk=None):
        """Add an item to a recipe"""
        try:
            serializer = RecipeItemCreateUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            response = self.get_service().add_recipe_item(pk, serializer.validated_data)
            
            if response.get('success', False):
                result_serializer = RecipeItemSerializer(response.get('data'))
                return Response({'success': True, 'data': result_serializer.data}, 
                                status=status.HTTP_201_CREATED)
            
            return Response(response, status=response.get('status_code', status.HTTP_400_BAD_REQUEST))
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecipeItemViewSet(viewsets.ModelViewSet):
    """ViewSet for RecipeItem operations"""
    queryset = RecipeItem.objects.all()
    serializer_class = RecipeItemSerializer
    filterset_fields = ['recipe_id', 'input_item_id']
    ordering_fields = ['sequence', 'created_at']
    ordering = ['sequence']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeItemCreateUpdateSerializer
        return RecipeItemSerializer
    
    def get_service(self):
        return RecipeService()
    
    def update(self, request, *args, **kwargs):
        try:
            recipe_item_id = kwargs.get('pk')
            
            # Partial update for PATCH
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            response = self.get_service().update_recipe_item(recipe_item_id, serializer.validated_data)
            
            if response.get('success', False):
                result_serializer = RecipeItemSerializer(response.get('data'))
                return Response({'success': True, 'data': result_serializer.data})
            
            return Response(response, status=response.get('status_code', status.HTTP_400_BAD_REQUEST))
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        try:
            recipe_item_id = kwargs.get('pk')
            response = self.get_service().delete_recipe_item(recipe_item_id)
            
            if response.get('success', False):
                return Response(response)
            
            return Response(response, status=response.get('status_code', status.HTTP_400_BAD_REQUEST))
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
