from django.db import models
from django.db import transaction
from apps.service.models import RepairPart
from apps.common.repositories.base_repository import BaseRepository


class RepairPartRepository(BaseRepository):
    """
    Repository for RepairPart model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(RepairPart)
    
    def get_by_repair(self, repair_id):
        """
        Get all repair parts for a specific repair request
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            QuerySet of repair parts
        """
        return self.model.objects.filter(repair_request_id=repair_id)
    
    def get_by_item(self, item_id):
        """
        Get all repair parts for a specific inventory item
        
        Args:
            item_id: Item ID
            
        Returns:
            QuerySet of repair parts
        """
        return self.model.objects.filter(item_id=item_id)
    
    def get_warranty_parts(self):
        """
        Get all warranty-covered repair parts
        
        Returns:
            QuerySet of warranty-covered repair parts
        """
        return self.model.objects.filter(is_warranty_covered=True)
    
    def get_non_warranty_parts(self):
        """
        Get all non-warranty repair parts
        
        Returns:
            QuerySet of non-warranty repair parts
        """
        return self.model.objects.filter(is_warranty_covered=False)
    
    def get_total_cost_for_repair(self, repair_id):
        """
        Calculate the total cost of all parts for a repair
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            Total cost of all parts
        """
        parts = self.get_by_repair(repair_id)
        return sum(part.total_price for part in parts)
    
    def get_total_cost_non_warranty_for_repair(self, repair_id):
        """
        Calculate the total cost of non-warranty parts for a repair
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            Total cost of non-warranty parts
        """
        parts = self.model.objects.filter(
            repair_request_id=repair_id,
            is_warranty_covered=False
        )
        return sum(part.total_price for part in parts)
    
    @transaction.atomic
    def create_multiple(self, parts_data):
        """
        Create multiple repair part records
        
        Args:
            parts_data: List of repair part data dictionaries
            
        Returns:
            List of created RepairPart instances
        """
        parts = []
        for data in parts_data:
            # Calculate total_price before creation
            data['total_price'] = data['quantity'] * data['unit_price']
            part = self.model.objects.create(**data)
            parts.append(part)
        
        # If we have a repair request, update its total cost
        if parts and 'repair_request_id' in parts_data[0]:
            repair_id = parts_data[0]['repair_request_id']
            from apps.service.repositories.repair_request_repository import RepairRequestRepository
            repair_repo = RepairRequestRepository()
            repair = repair_repo.get(id=repair_id)
            
            # Update repair cost based on non-warranty parts
            non_warranty_cost = self.get_total_cost_non_warranty_for_repair(repair_id)
            repair_repo.set_repair_cost(repair_id, non_warranty_cost)
        
        return parts
    
    @transaction.atomic
    def update_warranty_status(self, part_id, is_warranty_covered):
        """
        Update the warranty status of a repair part
        
        Args:
            part_id: Repair part ID
            is_warranty_covered: Whether the part is covered by warranty
            
        Returns:
            Updated RepairPart instance
        """
        part = self.get(id=part_id)
        part.is_warranty_covered = is_warranty_covered
        part.save()
        
        # Update repair request cost
        from apps.service.repositories.repair_request_repository import RepairRequestRepository
        repair_repo = RepairRequestRepository()
        non_warranty_cost = self.get_total_cost_non_warranty_for_repair(part.repair_request_id)
        repair_repo.set_repair_cost(part.repair_request_id, non_warranty_cost)
        
        return part