from django.shortcuts import get_object_or_404
from apps.inventory.models import Item


class ItemRepository:
    """
    Repository class for Item data access operations.
    Abstracts all database operations related to Item model.
    """
    
    def get_all_items(self):
        """Get all items ordered by name"""
        return Item.objects.all()
    
    def get_item_by_id(self, item_id):
        """Get a specific item by its ID"""
        return get_object_or_404(Item, id=item_id)
    
    def get_item_by_sku(self, sku):
        """Get a specific item by its SKU"""
        return get_object_or_404(Item, sku=sku)
    
    def get_items_by_category(self, category_id):
        """Get all items in a specific category"""
        return Item.objects.filter(category_id=category_id)
    
    def get_items_by_type(self, item_type):
        """Get all items of a specific type (RAW, INTERMEDIATE, FINAL)"""
        return Item.objects.filter(item_type=item_type)
    
    def create_item(self, item_data):
        """Create a new item"""
        return Item.objects.create(**item_data)
    
    def update_item(self, item_id, item_data):
        """Update an existing item"""
        item = self.get_item_by_id(item_id)
        
        for key, value in item_data.items():
            setattr(item, key, value)
        
        item.save()
        return item
    
    def delete_item(self, item_id):
        """Delete an item"""
        item = self.get_item_by_id(item_id)
        item.delete()
        return True
