from django.db import transaction
from apps.service.repositories.repair_part_repository import RepairPartRepository
from apps.service.repositories.repair_request_repository import RepairRequestRepository
from apps.inventory.repositories.item_repository import ItemRepository


class RepairPartService:
    """
    Service class to handle business logic for Repair Part operations.
    Uses RepairPartRepository for data access.
    """
    
    def __init__(
        self,
        repair_part_repository: RepairPartRepository = None,
        repair_request_repository: RepairRequestRepository = None,
        item_repository: ItemRepository = None
    ):
        self.repository = repair_part_repository or RepairPartRepository()
        self.repair_repository = repair_request_repository or RepairRequestRepository()
        self.item_repository = item_repository or ItemRepository()
    
    def get_parts_by_repair(self, repair_id):
        """
        Get all parts used in a specific repair
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            QuerySet of repair parts or None if repair not found
        """
        # Verify repair exists
        repair = self.repair_repository.get(id=repair_id)
        if not repair:
            return None
            
        return self.repository.get_by_repair(repair_id)
    
    def get_part(self, part_id):
        """
        Get a repair part by ID
        
        Args:
            part_id: Repair part ID
            
        Returns:
            RepairPart instance or None if not found
        """
        return self.repository.get(id=part_id)
    
    def get_most_used_parts(self, limit=10):
        """
        Get the most frequently used parts in repairs
        
        Args:
            limit: Number of parts to return
            
        Returns:
            List of items with usage count
        """
        return self.repository.get_most_used_parts(limit)
    
    def calculate_parts_cost(self, repair_id):
        """
        Calculate the total cost of parts used in a repair
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            Dictionary with cost information or None if repair not found
        """
        # Verify repair exists
        repair = self.repair_repository.get(id=repair_id)
        if not repair:
            return None
            
        parts = self.repository.get_by_repair(repair_id)
        total_cost = sum(part.cost * part.quantity for part in parts)
        
        return {
            'repair': repair,
            'parts_count': parts.count(),
            'total_parts_cost': total_cost,
            'parts': parts
        }
    
    @transaction.atomic
    def add_part_to_repair(self, repair_id, part_data):
        """
        Add a part to a repair
        
        Args:
            repair_id: Repair request ID
            part_data: Dictionary with part data
            
        Returns:
            Created RepairPart instance
            
        Raises:
            ValueError: When validation fails
        """
        # Validate repair exists
        repair = self.repair_repository.get(id=repair_id)
        if not repair:
            raise ValueError(f"Repair request with ID {repair_id} not found")
            
        # Validate item exists if item_id is provided
        if 'item_id' in part_data:
            item = self.item_repository.get(id=part_data['item_id'])
            if not item:
                raise ValueError(f"Item with ID {part_data['item_id']} not found")
        
        # Set repair_id in part data
        part_data['repair_id'] = repair_id
        
        # Create part
        return self.repository.create(**part_data)
    
    @transaction.atomic
    def add_multiple_parts(self, repair_id, parts_data):
        """
        Add multiple parts to a repair
        
        Args:
            repair_id: Repair request ID
            parts_data: List of dictionaries with part data
            
        Returns:
            List of created RepairPart instances
            
        Raises:
            ValueError: When validation fails
        """
        # Validate repair exists
        repair = self.repair_repository.get(id=repair_id)
        if not repair:
            raise ValueError(f"Repair request with ID {repair_id} not found")
        
        # Validate all items exist
        for part_data in parts_data:
            if 'item_id' in part_data:
                item = self.item_repository.get(id=part_data['item_id'])
                if not item:
                    raise ValueError(f"Item with ID {part_data['item_id']} not found")
            
            # Set repair_id in part data
            part_data['repair_id'] = repair_id
        
        # Create parts
        return self.repository.create_multiple(parts_data)
    
    def update_part(self, part_id, part_data):
        """
        Update a repair part
        
        Args:
            part_id: Repair part ID
            part_data: Dictionary with updated part data
            
        Returns:
            Updated RepairPart instance
            
        Raises:
            ValueError: When validation fails
        """
        part = self.repository.get(id=part_id)
        if not part:
            return None
        
        # Validate item exists if changing
        if 'item_id' in part_data:
            item = self.item_repository.get(id=part_data['item_id'])
            if not item:
                raise ValueError(f"Item with ID {part_data['item_id']} not found")
                
        return self.repository.update(part, **part_data)
    
    def remove_part(self, part_id):
        """
        Remove a part from a repair
        
        Args:
            part_id: Repair part ID
            
        Returns:
            Boolean indicating success
        """
        part = self.repository.get(id=part_id)
        if not part:
            return False
            
        return self.repository.delete(part)