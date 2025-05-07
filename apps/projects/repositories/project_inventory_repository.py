from apps.common.repositories.base_repository import BaseRepository
from apps.projects.models import ProjectInventory
from django.db import models


class ProjectInventoryRepository(BaseRepository):
    """
    Repository for ProjectInventory model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(ProjectInventory)
    
    def get_project_inventory(self, project_id, item_id=None):
        """
        Get inventory items for a specific project.
        
        Args:
            project_id (uuid): Project ID
            item_id (uuid, optional): Filter by specific item
            
        Returns:
            QuerySet: Filtered project inventory items
        """
        filters = {'project': project_id}
        
        if item_id:
            filters['item'] = item_id
            return self.get(**filters)
        
        return self.filter(**filters)
    
    def get_low_stock_items(self, project_id):
        """
        Get project inventory items with stock level below minimum.
        
        Args:
            project_id (uuid): Project ID
            
        Returns:
            QuerySet: Low stock items for the project
        """
        return self.filter(
            project=project_id,
            quantity__lt=models.F('minimum_stock_level')
        )
    
    def update_quantity(self, project_id, item_id, quantity_change):
        """
        Update the quantity of an item in project inventory.
        
        Args:
            project_id (uuid): Project ID
            item_id (uuid): Item ID
            quantity_change (int): Amount to add (positive) or subtract (negative)
            
        Returns:
            ProjectInventory: Updated inventory item
        """
        inventory_item = self.get(project=project_id, item=item_id)
        inventory_item.quantity += quantity_change
        return self.update(inventory_item.id, {'quantity': inventory_item.quantity})
