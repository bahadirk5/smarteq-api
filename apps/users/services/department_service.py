from typing import List, Optional, Dict, Any
from apps.users.models.department import Department
from apps.users.repositories.department_repository import DepartmentRepository

class DepartmentService:
    def __init__(self, department_repository: DepartmentRepository = None):
        self.department_repository = department_repository or DepartmentRepository()
    
    def get_department(self, department_id: int) -> Optional[Department]:
        return self.department_repository.get_by_id(department_id)
    
    def get_department_by_name(self, name: str) -> Optional[Department]:
        return self.department_repository.get_by_name(name)
    
    def list_departments(self) -> List[Department]:
        return self.department_repository.list()
    
    def list_departments_with_roles(self) -> List[Department]:
        return self.department_repository.list_with_roles()
    
    def create_department(self, name: str, description: str = None) -> Department:
        department_data = {
            "name": name,
        }
        if description:
            department_data["description"] = description
            
        return self.department_repository.create(**department_data)
    
    def update_department(self, department_id: int, **update_data) -> Optional[Department]:
        department = self.get_department(department_id)
        if not department:
            return None
        
        return self.department_repository.update(department, **update_data)
    
    def delete_department(self, department_id: int) -> bool:
        department = self.get_department(department_id)
        if not department:
            return False
        
        return self.department_repository.delete(department)