from typing import List, Optional
from apps.users.models.role import Role
from apps.users.repositories.base_repository import BaseRepository

class RoleRepository(BaseRepository):
    def __init__(self):
        super().__init__(Role)
    
    def get_by_name(self, name: str) -> Optional[Role]:
        try:
            return self.get_queryset().get(name=name)
        except Role.DoesNotExist:
            return None
    
    def get_by_name_and_department(self, name: str, department_id: int) -> Optional[Role]:
        try:
            return self.get_queryset().get(name=name, department_id=department_id)
        except Role.DoesNotExist:
            return None
    
    def list_by_department(self, department_id: int) -> List[Role]:
        return list(self.get_queryset().filter(department_id=department_id))