from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.responses import success_response, error_response
from apps.projects.serializers.project_inventory_serializer import (
    ProjectInventorySerializer, ProjectInventoryDetailSerializer
)
from apps.projects.services.project_inventory_service import ProjectInventoryService

class ProjectInventoryViewSet(viewsets.ViewSet):
    """
    Proje envanter işlemleri için katmanlı mimariye uygun ViewSet.
    Tüm iş mantığı servis katmanında, DB işlemleri repository katmanında.
    """
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'item']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ProjectInventoryService()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ProjectInventoryDetailSerializer
        return ProjectInventorySerializer

    def list(self, request):
        try:
            # Check if there's a project filter
            project_id = request.query_params.get('project')
            if project_id:
                inventories = self.service.get_project_inventory(project_id)
            else:
                inventories = self.service.get_all_project_inventory()
            
            serializer = self.get_serializer_class()(inventories, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))

    def retrieve(self, request, pk=None):
        """Get a specific project inventory by ID"""
        try:
            inventory = self.service.get_project_inventory_by_id(pk)
            serializer = self.get_serializer_class()(inventory)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            try:
                inventory = self.service.create_project_inventory(serializer.validated_data)
                return success_response(data=self.get_serializer_class()(inventory).data, status_code=status.HTTP_201_CREATED)
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)

    def update(self, request, pk=None):
        try:
            inventory = self.service.get_project_inventory_by_id(pk)
            serializer = self.get_serializer_class()(instance=inventory, data=request.data)
            if serializer.is_valid():
                inventory = self.service.update_project_inventory(pk, serializer.validated_data)
                return success_response(data=self.get_serializer_class()(inventory).data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))

    def partial_update(self, request, pk=None):
        try:
            inventory = self.service.get_project_inventory_by_id(pk)
            serializer = self.get_serializer_class()(instance=inventory, data=request.data, partial=True)
            if serializer.is_valid():
                inventory = self.service.update_project_inventory(pk, serializer.validated_data)
                return success_response(data=self.get_serializer_class()(inventory).data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))

    def destroy(self, request, pk=None):
        try:
            self.service.delete_project_inventory(pk)
            return success_response()
        except Exception as e:
            return error_response(str(e))

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        project_id = request.query_params.get('project')
        if not project_id:
            return error_response("Project ID is required", status_code=status.HTTP_400_BAD_REQUEST)
        try:
            low_stock_items = self.service.get_low_stock_items(project_id)
            serializer = ProjectInventoryDetailSerializer(low_stock_items, many=True)
            return success_response(serializer.data)
        except Exception as e:
            return error_response(str(e))

    @action(detail=False, url_path='by_project/(?P<project_id>[^/.]+)', methods=['get'])
    def by_project(self, request, project_id=None):
        """Get all inventory items for a specific project"""
        if not project_id:
            return error_response("Project ID is required")
        try:
            inventories = self.service.get_project_inventory(project_id)
            serializer = self.get_serializer_class()(inventories, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        from_project_id = request.data.get('from_project_id')
        to_project_id = request.data.get('to_project_id')
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        notes = request.data.get('notes')

        if not all([from_project_id, to_project_id, item_id, quantity]):
            return error_response("from_project_id, to_project_id, item_id, and quantity are required", status_code=status.HTTP_400_BAD_REQUEST)
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            source_item, dest_item = self.service.transfer_item(
                from_project_id, to_project_id, item_id, quantity, notes
            )
            return success_response({
                'source': ProjectInventoryDetailSerializer(source_item).data,
                'destination': ProjectInventoryDetailSerializer(dest_item).data
            })
        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(f"Transfer failed: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Not: İleride permission_classes, filter_backends, search, ordering eklenebilir.
