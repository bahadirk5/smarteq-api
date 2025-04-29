from apps.inventory.repositories.item_repository import ItemRepository


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
    
    def delete_item(self, item_id):
        """Delete an item"""
        # Here we could check if the item is used in any BOMs, production processes etc.
        # and prevent deletion if necessary
        return self.repository.delete_item(item_id)
