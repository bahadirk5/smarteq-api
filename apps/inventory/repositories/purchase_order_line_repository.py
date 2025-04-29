from django.shortcuts import get_object_or_404
from apps.inventory.models import PurchaseOrderLine


class PurchaseOrderLineRepository:
    """
    Repository class for PurchaseOrderLine data access operations.
    Abstracts all database operations related to PurchaseOrderLine model.
    """
    
    def get_all_purchase_order_lines(self):
        """Get all purchase order lines"""
        return PurchaseOrderLine.objects.all()
    
    def get_purchase_order_line_by_id(self, line_id):
        """Get a specific purchase order line by ID"""
        return get_object_or_404(PurchaseOrderLine, id=line_id)
    
    def get_lines_by_purchase_order(self, purchase_order_id):
        """Get all lines for a specific purchase order"""
        return PurchaseOrderLine.objects.filter(purchase_order_id=purchase_order_id)
    
    def get_lines_by_item(self, item_id):
        """Get all purchase order lines for a specific item"""
        return PurchaseOrderLine.objects.filter(item_id=item_id)
    
    def create_purchase_order_line(self, line_data):
        """Create a new purchase order line"""
        return PurchaseOrderLine.objects.create(**line_data)
    
    def update_purchase_order_line(self, line_id, line_data):
        """Update an existing purchase order line"""
        line = self.get_purchase_order_line_by_id(line_id)
        
        for key, value in line_data.items():
            setattr(line, key, value)
        
        line.save()
        return line
    
    def delete_purchase_order_line(self, line_id):
        """Delete a purchase order line"""
        line = self.get_purchase_order_line_by_id(line_id)
        line.delete()
        return True
    
    def create_multiple_lines(self, purchase_order_id, lines_data):
        """Create multiple purchase order lines in a single transaction"""
        lines = []
        
        for line_data in lines_data:
            line_data['purchase_order_id'] = purchase_order_id
            line = PurchaseOrderLine.objects.create(**line_data)
            lines.append(line)
            
        return lines
