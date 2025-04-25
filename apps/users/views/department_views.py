from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.models import Department
from apps.users.serializers.department_serializers import DepartmentSerializer, DepartmentDetailSerializer
from apps.users.serializers.role_serializers import RoleSerializer
from apps.users.services import DepartmentService

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department_service = DepartmentService()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailSerializer
        return DepartmentSerializer
    
    def list(self, request, *args, **kwargs):
        departments = self.department_service.list_departments()
        serializer = self.get_serializer(departments, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        department = self.department_service.get_department(kwargs['pk'])
        if not department:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(department)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        department = self.department_service.create_department(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description')
        )
        
        result_serializer = self.get_serializer(department)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        department = self.department_service.get_department(kwargs['pk'])
        if not department:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(department, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        updated_department = self.department_service.update_department(
            department_id=kwargs['pk'],
            **serializer.validated_data
        )
        
        result_serializer = self.get_serializer(updated_department)
        return Response(result_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        department = self.department_service.get_department(kwargs['pk'])
        if not department:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        self.department_service.delete_department(kwargs['pk'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Get all roles for a specific department."""
        department = self.department_service.get_department(pk)
        if not department:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        
        roles = department.roles.filter(deleted_at__isnull=True)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)