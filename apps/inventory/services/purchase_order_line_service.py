from apps.inventory.repositories.purchase_order_line_repository import PurchaseOrderLineRepository
from apps.inventory.repositories.item_repository import ItemRepository


class PurchaseOrderLineService:
    """
    Service class to handle business logic for Purchase Order Line operations.
    Uses PurchaseOrderLineRepository for data access.
    """
    
    def __init__(self):
        self.repository = PurchaseOrderLineRepository()
        self.item_repository = ItemRepository()
    
    def get_all_purchase_order_lines(self):
        """Get all purchase order lines"""
        return self.repository.get_all_purchase_order_lines()
    
    def get_purchase_order_line(self, line_id):
        """Get a purchase order line by its ID"""
        return self.repository.get_purchase_order_line_by_id(line_id)
    
    def get_lines_by_purchase_order(self, purchase_order_id):
        """Get all lines for a specific purchase order"""
        lines = self.repository.get_lines_by_purchase_order(purchase_order_id)
        
        # Calculate purchase order summary
        total_amount = sum(line.total_price for line in lines)
        
        return {
            'lines': lines,
            'total_amount': total_amount,
            'total_items': lines.count()
        }
    
    def get_purchased_items_history(self, item_id):
        """Get the purchase history for a specific item"""
        # Ensure the item exists
        item = self.item_repository.get_item_by_id(item_id)
        
        # Get purchase lines for this item
        purchase_lines = self.repository.get_lines_by_item(item_id)
        
        return purchase_lines
    
    def create_purchase_order_line(self, line_data):
        """Create a new purchase order line"""
        # Validate that the item exists
        item = self.item_repository.get_item_by_id(line_data['item_id'])
        
        # Additional validation could be done here
        return self.repository.create_purchase_order_line(line_data)
    
    def update_purchase_order_line(self, line_id, line_data):
        """Update an existing purchase order line"""
        # If item_id is being updated, validate that the new item exists
        if 'item_id' in line_data:
            self.item_repository.get_item_by_id(line_data['item_id'])
        
        return self.repository.update_purchase_order_line(line_id, line_data)
    
    def delete_purchase_order_line(self, line_id):
        """Delete a purchase order line"""
        return self.repository.delete_purchase_order_line(line_id)
    
    def create_multiple_lines(self, purchase_order_id, lines_data):
        """Create multiple purchase order lines for a purchase order"""
        # Validate all items first
        for line_data in lines_data:
            self.item_repository.get_item_by_id(line_data['item_id'])
        
        return self.repository.create_multiple_lines(purchase_order_id, lines_data)
