from apps.inventory.repositories.item_repository import ItemRepository
from apps.projects.repositories.project_inventory_repository import ProjectInventoryRepository
from apps.projects.services.project_inventory_service import ProjectInventoryService
from django.db import transaction


class ItemService:
    """
    Service class to handle business logic for Item operations.
    Uses ItemRepository for data access.
    """
    
    def __init__(self):
        self.repository = ItemRepository()
    
    def get_all_items(self):
        """Get all items"""
        return self.repository.get_all_items()
    
    def get_item(self, item_id):
        """Get an item by its ID"""
        return self.repository.get_item_by_id(item_id)
    
    def get_item_by_sku(self, sku):
        """Get an item by its SKU"""
        return self.repository.get_item_by_sku(sku)
    
    def get_items_by_category(self, category_id):
        """Get all items in a category"""
        return self.repository.get_items_by_category(category_id)
    
    def get_items_by_type(self, item_type):
        """Get all items of a specific type"""
        if item_type not in ['RAW', 'INTERMEDIATE', 'FINAL']:
            raise ValueError(f"Invalid item type: {item_type}. Must be one of: RAW, INTERMEDIATE, FINAL")
        return self.repository.get_items_by_type(item_type)
    
    def get_raw_materials(self):
        """Get all raw materials"""
        return self.repository.get_items_by_type('RAW')
    
    def get_intermediate_products(self):
        """Get all intermediate products"""
        return self.repository.get_items_by_type('INTERMEDIATE')
    
    def get_final_products(self):
        """Get all final products"""
        return self.repository.get_items_by_type('FINAL')
    
    def create_item(self, item_data):
        """Create a new item"""
        # Validate item type
        if item_data.get('item_type') not in ['RAW', 'INTERMEDIATE', 'FINAL']:
            raise ValueError(f"Invalid item type: {item_data.get('item_type')}. Must be one of: RAW, INTERMEDIATE, FINAL")
        
        # Additional validation could be added here
        return self.repository.create_item(item_data)
    
    def update_item(self, item_id, item_data):
        """Update an existing item"""
        # Validate item type if provided
        if 'item_type' in item_data and item_data['item_type'] not in ['RAW', 'INTERMEDIATE', 'FINAL']:
            raise ValueError(f"Invalid item type: {item_data['item_type']}. Must be one of: RAW, INTERMEDIATE, FINAL")
        
        return self.repository.update_item(item_id, item_data)
    
    def update_item_quantity(self, item_id, quantity):
        """Update the quantity of an item"""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Quantity must be a valid integer")
            
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
            
        return self.repository.update_item_quantity(item_id, quantity)
        
    def get_item_quantity(self, item_id):
        """Get the current quantity of an item"""
        return self.repository.get_item_quantity(item_id)
    
    def delete_item(self, item_id):
        """Delete an item"""
        # Here we could check if the item is used in any BOMs, production processes etc.
        # and prevent deletion if necessary
        return self.repository.delete_item(item_id)
    
    @transaction.atomic
    def create_item_with_project(self, item_data, project_id=None, quantity=0, minimum_stock_level=0, notes=None):
        """Create a new item and optionally assign it to a project.
        
        Args:
            item_data (dict): Item data for creation
            project_id (int, optional): Project to assign the item to
            quantity (int, optional): Initial quantity in the project inventory
            minimum_stock_level (int, optional): Minimum stock level for project inventory
            notes (str, optional): Notes for project inventory
            
        Returns:
            Item: Created item object
            
        Raises:
            ValueError: If item type is invalid or project_id is invalid
        """
        # Validate item type
        if item_data.get('item_type') not in ['RAW', 'INTERMEDIATE', 'FINAL']:
            raise ValueError(f"Invalid item type: {item_data.get('item_type')}. Must be one of: RAW, INTERMEDIATE, FINAL")
        
        # Create the item
        item = self.repository.create_item(item_data)
        
        # If project_id is provided, assign the item to the project using service layer
        if project_id:
            try:
                project_inventory_service = ProjectInventoryService()
                project_inventory_service.add_item_to_project(
                    project_id=project_id,
                    item_id=item.id,
                    quantity=quantity,
                    minimum_stock_level=minimum_stock_level,
                    notes=notes
                )
            except Exception as e:
                # Since we're in a transaction, this will roll back the item creation
                # if there's any issue with the project inventory
                raise ValueError(f"Could not assign item to project: {str(e)}")
        
        return item
