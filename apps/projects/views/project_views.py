# apps/projects/views/project_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.projects.models.project import Project
from apps.projects.serializers.project_serializer import ProjectSerializer
from apps.projects.services.project_service import ProjectService
from apps.common.permissions import IsSystemAdminOrSoftwareDeveloper
from apps.common.responses import success_response, error_response

class ProjectViewSet(viewsets.ViewSet):
    """
    Proje işlemleri için katmanlı mimariye uygun ViewSet.
    Tüm iş mantığı servis katmanında, DB işlemleri repository katmanında.
    """
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSystemAdminOrSoftwareDeveloper()]
        return super().get_permissions()

    def list(self, request):
        projects = ProjectService().list_projects()
        serializer = ProjectSerializer(projects, many=True)
        return success_response(data=serializer.data)

    def retrieve(self, request, pk=None):
        project = ProjectService().get_project(pk)
        serializer = ProjectSerializer(project)
        return success_response(data=serializer.data)

    def create(self, request):
        self.check_permissions(request)
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = ProjectService().create_project(serializer.validated_data)
        return success_response(data=ProjectSerializer(project).data, status_code=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        self.check_permissions(request)
        project = ProjectService().get_project(pk)  # Önce mevcut projeyi al
        serializer = ProjectSerializer(instance=project, data=request.data)
        serializer.is_valid(raise_exception=True)
        project = ProjectService().update_project(pk, serializer.validated_data)
        return success_response(data=ProjectSerializer(project).data)

    def partial_update(self, request, pk=None):
        self.check_permissions(request)
        project = ProjectService().get_project(pk)  # Önce mevcut projeyi al
        serializer = ProjectSerializer(instance=project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = ProjectService().update_project(pk, serializer.validated_data)
        return success_response(data=ProjectSerializer(project).data)

    def destroy(self, request, pk=None):
        self.check_permissions(request)
        ProjectService().delete_project(pk)
        return success_response(status_code=status.HTTP_204_NO_CONTENT)
# İleride permission_classes, filter_backends, search, ordering eklenebilir
