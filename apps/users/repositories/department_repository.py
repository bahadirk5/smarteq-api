from typing import List, Optional
from apps.users.models.department import Department
from apps.users.repositories.base_repository import BaseRepository

class DepartmentRepository(BaseRepository):
    def __init__(self):
        self.model = Department
    
    def get_by_name(self, name: str) -> Optional[Department]:
        try:
            return self.get_queryset().get(name=name)
        except Department.DoesNotExist:
            return None
    
    def list_with_roles(self) -> List[Department]:
        return list(self.get_queryset().prefetch_related('roles'))