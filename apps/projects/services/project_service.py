# apps/projects/services/project_service.py
from apps.projects.models.project import Project
from apps.projects.repositories.project_repository import ProjectRepository

class ProjectService:
    def __init__(self):
        self.repository = ProjectRepository()

    def create_project(self, data):
        return self.repository.create(**data)

    def list_projects(self):
        return self.repository.list()

    def get_project(self, pk):
        return self.repository.get(pk=pk)

    def update_project(self, pk, data):
        return self.repository.update(pk, **data)

    def delete_project(self, pk):
        return self.repository.delete(pk)
