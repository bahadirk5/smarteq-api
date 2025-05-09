from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import traceback

from apps.inventory.models.production import Production
from apps.inventory.models.production_item import ProductionItem
from apps.inventory.models.production_history import ProductionHistory
from apps.inventory.serializers.production_serializers import (
    ProductionSerializer, ProductionDetailSerializer, ProductionCreateSerializer, ProductionUpdateSerializer,
    ProductionItemSerializer, ProductionHistorySerializer
)
from apps.inventory.services.production_service import ProductionService
from apps.inventory.utils.logger import LoggerMixin


# Configure logger
logger = logging.getLogger('apps.inventory.ProductionViewSet')


class ProductionViewSet(viewsets.ModelViewSet, LoggerMixin):
    """ViewSet for Production operations"""
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    filterset_fields = ['recipe_id', 'executed_by_id']
    search_fields = ['notes']
    ordering_fields = ['execution_date', 'created_at']
    ordering = ['-execution_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductionDetailSerializer
        elif self.action == 'create':
            return ProductionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductionUpdateSerializer
        return ProductionSerializer
    
    def get_service(self):
        return ProductionService()
    
    def list(self, request, *args, **kwargs):
        try:
            self.log_info("Getting all productions")
            
            # Extract query parameters
            filters = {}
            if 'recipe_id' in request.query_params:
                filters['recipe_id'] = request.query_params.get('recipe_id')
                self.log_debug(f"Filtering by recipe ID: {filters['recipe_id']}")
                
            if 'executed_by_id' in request.query_params:
                filters['executed_by_id'] = request.query_params.get('executed_by_id')
                self.log_debug(f"Filtering by user ID: {filters['executed_by_id']}")
                
            if 'date_from' in request.query_params:
                filters['date_from'] = request.query_params.get('date_from')
                self.log_debug(f"Filtering by date from: {filters['date_from']}")
                
            if 'date_to' in request.query_params:
                filters['date_to'] = request.query_params.get('date_to')
                self.log_debug(f"Filtering by date to: {filters['date_to']}")
            
            # Use service to get productions
            self.log_debug(f"Calling service with filters: {filters}")
            service_response = self.get_service().get_all_productions(filters)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                serializer = self.get_serializer(response_data.get('data'), many=True)
                self.log_debug(f"Returning {len(serializer.data)} productions")
                return Response({
                    'data': serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            self.log_warning(f"Service returned error: {response_data.get('error')}")
            return service_response
        except Exception as e:
            self.log_exception(f"Exception in list view: {str(e)}")
            tb = traceback.format_exc()
            self.log_error(f"Traceback: {tb}")
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            production_id = kwargs.get('pk')
            self.log_info(f"Retrieving production with ID: {production_id}")
            
            service_response = self.get_service().get_production_by_id(production_id)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                serializer = self.get_serializer(response_data.get('data'))
                self.log_debug(f"Successfully retrieved production: {production_id}")
                return Response({
                    'data': serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            self.log_warning(f"Service returned error for production {production_id}: {response_data.get('error')}")
            return service_response
        except Exception as e:
            self.log_exception(f"Exception in retrieve view for production {kwargs.get('pk')}: {str(e)}")
            tb = traceback.format_exc()
            self.log_error(f"Traceback: {tb}")
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        try:
            self.log_info(f"Creating new production with data: {request.data}")
            
            # Authentication check
            if not request.user or not request.user.is_authenticated:
                error_msg = "Authentication required to create productions"
                self.log_error(error_msg)
                return Response({
                    'data': None,
                    'error': error_msg,
                    'status': status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Validate data with serializer
            serializer = self.get_serializer(data=request.data)
            
            # Log validation details if there are errors
            if not serializer.is_valid():
                self.log_error(f"Validation errors: {serializer.errors}")
                return Response({
                    'data': None, 
                    'error': serializer.errors, 
                    'status': status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.log_debug(f"Data validation successful. Calling service with validated data: {serializer.validated_data}")
            
            # Call service with validated data
            service_response = self.get_service().create_production(serializer.validated_data, request.user)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                result_serializer = ProductionDetailSerializer(response_data.get('data'))
                self.log_info(f"Production created successfully with ID: {result_serializer.data.get('id')}")
                return Response({
                    'data': result_serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            self.log_warning(f"Service returned error during creation: {response_data.get('error')}")
            return service_response
        except Exception as e:
            self.log_exception(f"Exception in create view: {str(e)}")
            tb = traceback.format_exc()
            self.log_error(f"Traceback: {tb}")
            return Response({
                'data': None,
                'error': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        try:
            production_id = kwargs.get('pk')
            
            # Partial update for PATCH
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            service_response = self.get_service().update_production(production_id, serializer.validated_data, request.user)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                result_serializer = ProductionDetailSerializer(response_data.get('data'))
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
    
    @action(detail=True, methods=['get'], url_path='history')
    def production_history(self, request, pk=None):
        """Get history records for a production"""
        try:
            service_response = self.get_service().get_production_history(pk)
            
            # Extract data directly from ApiResponse
            response_data = service_response.data
            status_code = service_response.status_code
            
            # If successful, serialize and return data
            if response_data.get('data') is not None:
                serializer = ProductionHistorySerializer(response_data.get('data'), many=True)
                return Response({
                    'data': serializer.data,
                    'error': None,
                    'status': status_code
                }, status=status_code)
            
            # Otherwise return the error response directly
            return service_response
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, url_path='by_recipe/(?P<recipe_id>[^/.]+)', methods=['get'])
    def by_recipe(self, request, recipe_id=None):
        """Get all productions for a specific recipe using path parameter"""
        try:
            filters = {'recipe_id': recipe_id}
            service_response = self.get_service().get_all_productions(filters)
            
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
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
