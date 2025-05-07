from django.db import transaction
from apps.projects.repositories.project_inventory_repository import ProjectInventoryRepository
from apps.inventory.repositories.item_repository import ItemRepository
from apps.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository


class ProjectInventoryService:
    """
    Service class to handle business logic for project inventory operations.
    Follows the service pattern for encapsulating business logic.
    """
    
    def __init__(self):
        self.repository = ProjectInventoryRepository()
        self.item_repository = ItemRepository()
        self.transaction_repository = InventoryTransactionRepository()

    def get_all_project_inventory(self):
        """
        Get all project inventory items.
        
        Returns:
            QuerySet: All project inventory items
        """
        return self.repository.list()
        
    def get_project_inventory_by_id(self, inventory_id):
        """
        Get project inventory item by ID.
        
        Args:
            inventory_id (int): Project inventory ID
            
        Returns:
            ProjectInventory: Project inventory item
        """
        return self.repository.get(id=inventory_id)
    
    def get_project_inventory(self, project_id, item_id=None):
        """
        Get inventory items for a project.
        
        Args:
            project_id (int): Project ID
            item_id (int, optional): Optional item ID to filter by
            
        Returns:
            QuerySet or ProjectInventory: Project inventory items
        """
        return self.repository.get_project_inventory(project_id, item_id)
    
    def get_low_stock_items(self, project_id):
        """
        Get project inventory items with stock below minimum level.
        
        Args:
            project_id (int): Project ID
            
        Returns:
            QuerySet: Low stock inventory items
        """
        return self.repository.get_low_stock_items(project_id)
    
    def update_project_inventory(self, inventory_id, data):
        """
        Update a project inventory item.
        
        Args:
            inventory_id (int): Project inventory ID
            data (dict): Updated data
            
        Returns:
            ProjectInventory: Updated project inventory item
        """
        return self.repository.update(inventory_id, data)
        
    def delete_project_inventory(self, inventory_id):
        """
        Delete a project inventory item.
        
        Args:
            inventory_id (int): Project inventory ID
        """
        return self.repository.delete(inventory_id)
    
    @transaction.atomic
    def add_item_to_project(self, project_id, item_id, quantity, minimum_stock_level=0, notes=None):
        """
        Add or update an item in project inventory.
        
        Args:
            project_id (int): Project ID
            item_id (int): Item ID
            quantity (int): Initial quantity
            minimum_stock_level (int): Minimum stock threshold
            notes (str): Optional notes
            
        Returns:
            ProjectInventory: Created or updated inventory item
        """
        try:
            # Check if item already exists in project inventory
            inventory_item = self.repository.get_project_inventory(project_id, item_id)
            # Update existing item
            update_data = {
                'quantity': inventory_item.quantity + quantity,
                'minimum_stock_level': minimum_stock_level,
                'notes': notes or inventory_item.notes
            }
            return self.repository.update(inventory_item.id, update_data)
        except:
            # Create new project inventory item
            data = {
                'project_id': project_id,
                'item_id': item_id,
                'quantity': quantity,
                'minimum_stock_level': minimum_stock_level,
                'notes': notes
            }
            return self.repository.create(**data)  # data sözlüğünü unpacking yaparak keyword argümanlar olarak geçiriyoruz
    
    @transaction.atomic
    def transfer_item(self, from_project_id, to_project_id, item_id, quantity, notes=None):
        """
        Transfer an item from one project to another.
        
        Args:
            from_project_id (int): Source project ID
            to_project_id (int): Destination project ID
            item_id (int): Item ID to transfer
            quantity (int): Quantity to transfer
            notes (str): Optional notes for the transaction
            
        Returns:
            tuple: (source inventory item, destination inventory item)
        """
        # Validate quantity is positive
        if quantity <= 0:
            raise ValueError("Transfer quantity must be positive")
        
        # Get source inventory item
        source_item = self.repository.get_project_inventory(from_project_id, item_id)
        
        # Check if source has enough quantity
        if source_item.quantity < quantity:
            raise ValueError(f"Insufficient quantity in source project. Available: {source_item.quantity}")
        
        # Reduce quantity in source project
        source_item = self.repository.update_quantity(from_project_id, item_id, -quantity)
        
        # Add quantity to destination project
        try:
            dest_item = self.repository.get_project_inventory(to_project_id, item_id)
            dest_item = self.repository.update_quantity(to_project_id, item_id, quantity)
        except:
            # Item doesn't exist in destination project, create it
            dest_item = self.add_item_to_project(
                to_project_id, 
                item_id, 
                quantity,
                notes=f"Transferred from project ID: {from_project_id}"
            )
            
        # Record transactions
        transfer_note = notes or f"Transfer from project {from_project_id} to project {to_project_id}"
        
        # Source transaction (negative)
        self.transaction_repository.create_transaction({
            'item_id': item_id,
            'transaction_type': 'TRANSFER',
            'quantity': -quantity,
            'reference_model': 'ProjectInventory',
            'reference_id': source_item.id,
            'notes': f"OUT: {transfer_note}"
        })
        
        # Destination transaction (positive)
        self.transaction_repository.create_transaction({
            'item_id': item_id,
            'transaction_type': 'TRANSFER',
            'quantity': quantity,
            'reference_model': 'ProjectInventory',
            'reference_id': dest_item.id,
            'notes': f"IN: {transfer_note}"
        })
        
        return (source_item, dest_item)
