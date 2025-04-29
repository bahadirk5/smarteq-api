from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.inventory.serializers import (
    ProductionProcessSerializer, ProductionProcessListSerializer,
    ProductionProcessDetailSerializer, ProcessItemInputSerializer,
    ProcessItemInputDetailSerializer, ProcessItemOutputSerializer,
    ProcessItemOutputDetailSerializer, ProductionProcessSummarySerializer
)
from apps.inventory.services import ProductionProcessService
from apps.common.responses import success_response, error_response


class ProductionProcessViewSet(viewsets.ViewSet):
    """API endpoints for managing Production Processes."""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductionProcessService()
    
    def list(self, request):
        """Get all production processes"""
        processes = self.service.get_all_processes()
        serializer = ProductionProcessListSerializer(processes, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get a specific production process by ID"""
        try:
            process = self.service.get_process(pk)
            serializer = ProductionProcessDetailSerializer(process)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    def create(self, request):
        """Create a new production process"""
        serializer = ProductionProcessSerializer(data=request.data)
        if serializer.is_valid():
            try:
                process = self.service.create_process(serializer.validated_data)
                result_serializer = ProductionProcessDetailSerializer(process)
                return success_response(
                    data=result_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def update(self, request, pk=None):
        """Update an existing production process"""
        serializer = ProductionProcessSerializer(data=request.data)
        if serializer.is_valid():
            try:
                process = self.service.repository.update_process(pk, serializer.validated_data)
                result_serializer = ProductionProcessDetailSerializer(process)
                return success_response(data=result_serializer.data)
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    def partial_update(self, request, pk=None):
        """Partially update an existing production process"""
        try:
            process = self.service.get_process(pk)
            serializer = ProductionProcessSerializer(process, data=request.data, partial=True)
            if serializer.is_valid():
                updated_process = self.service.repository.update_process(pk, serializer.validated_data)
                result_serializer = ProductionProcessDetailSerializer(updated_process)
                return success_response(data=result_serializer.data)
            return error_response(serializer.errors)
        except Exception as e:
            return error_response(str(e))
    
    def destroy(self, request, pk=None):
        """Delete a production process"""
        try:
            self.service.repository.delete_process(pk)
            return success_response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get detailed information about a production process including inputs and outputs"""
        try:
            process_details = self.service.get_process_details(pk)
            serializer = ProductionProcessSummarySerializer(process_details['process'])
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a production process"""
        try:
            start_date = request.data.get('start_date')
            process = self.service.start_process(pk, start_date)
            serializer = ProductionProcessDetailSerializer(process)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a production process"""
        try:
            end_date = request.data.get('end_date')
            process = self.service.complete_process(pk, end_date)
            serializer = ProductionProcessDetailSerializer(process)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a production process"""
        try:
            process = self.service.cancel_process(pk)
            serializer = ProductionProcessDetailSerializer(process)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=True, methods=['post'])
    def add_input(self, request, pk=None):
        """Add an input to a production process"""
        serializer = ProcessItemInputSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Remove process_id from serializer as it comes from URL
                input_data = {k: v for k, v in serializer.validated_data.items() if k != 'process'}
                input_record = self.service.add_process_input(pk, input_data)
                result_serializer = ProcessItemInputDetailSerializer(input_record)
                return success_response(
                    data=result_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    @action(detail=True, methods=['post'])
    def add_output(self, request, pk=None):
        """Add an output to a production process"""
        serializer = ProcessItemOutputSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Remove process_id from serializer as it comes from URL
                output_data = {k: v for k, v in serializer.validated_data.items() if k != 'process'}
                output_record = self.service.add_process_output(pk, output_data)
                result_serializer = ProcessItemOutputDetailSerializer(output_record)
                return success_response(
                    data=result_serializer.data,
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response(serializer.errors)
    
    @action(detail=True, methods=['get'])
    def suggest_inputs(self, request, pk=None):
        """Suggest inputs for a production process based on its BOM"""
        try:
            suggested_inputs = self.service.suggest_inputs_from_bom(pk)
            return success_response(data=suggested_inputs)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active production processes"""
        try:
            processes = self.service.get_active_processes()
            serializer = ProductionProcessListSerializer(processes, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get all production processes for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return error_response('project_id parameter is required')
            
        try:
            processes = self.service.get_processes_by_project(project_id)
            serializer = ProductionProcessListSerializer(processes, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get all production processes with a specific status"""
        status_param = request.query_params.get('status')
        if not status_param:
            return error_response('status parameter is required')
            
        try:
            processes = self.service.get_processes_by_status(status_param)
            serializer = ProductionProcessListSerializer(processes, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(str(e))
