from typing import List, Optional, Dict, Any
from apps.users.models.role import Role
from apps.users.repositories.role_repository import RoleRepository
from apps.users.repositories.department_repository import DepartmentRepository

class RoleService:
    def __init__(
        self, 
        role_repository: RoleRepository = None,
        department_repository: DepartmentRepository = None
    ):
        self.role_repository = role_repository or RoleRepository()
        self.department_repository = department_repository or DepartmentRepository()
    
    def get_role(self, role_id: int) -> Optional[Role]:
        return self.role_repository.get_by_id(role_id)
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.role_repository.get_by_name(name)
    
    def get_role_by_name_and_department(self, name: str, department_id: int) -> Optional[Role]:
        return self.role_repository.get_by_name_and_department(name, department_id)
    
    def list_roles(self) -> List[Role]:
        return self.role_repository.list()
    
    def list_roles_by_department(self, department_id: int) -> List[Role]:
        return self.role_repository.list_by_department(department_id)
    
    def create_role(self, name: str, department_id: int, description: str = None) -> Optional[Role]:
        # Check if department exists
        department = self.department_repository.get_by_id(department_id)
        if not department:
            return None
        
        role_data = {
            "name": name,
            "department_id": department_id,
        }
        if description:
            role_data["description"] = description
            
        return self.role_repository.create(**role_data)
    
    def update_role(self, role_id: int, **update_data) -> Optional[Role]:
        role = self.get_role(role_id)
        if not role:
            return None
        
        # If department_id is being updated, check if the department exists
        if "department_id" in update_data:
            department = self.department_repository.get_by_id(update_data["department_id"])
            if not department:
                return None
        
        return self.role_repository.update(role, **update_data)
    
    def delete_role(self, role_id: int) -> bool:
        role = self.get_role(role_id)
        if not role:
            return False
        
        return self.role_repository.delete(role)