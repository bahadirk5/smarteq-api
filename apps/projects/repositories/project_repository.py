# apps/projects/repositories/project_repository.py
from apps.projects.models.project import Project
from apps.common.repositories.base_repository import BaseRepository

class ProjectRepository(BaseRepository):
    model = Project
