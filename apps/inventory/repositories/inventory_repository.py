from django.db.models import F, Sum
from apps.inventory.models.inventory_transaction import InventoryTransaction
from apps.inventory.models.item import Item


class InventoryRepository:
    """Repository for inventory management and tracking operations"""
    
    @staticmethod
    def get_item_quantity(item_id):
        """Get the current available quantity of an item"""
        try:
            # Get item details directly from Item table
            item = Item.objects.get(id=item_id)
            
            return {
                'item_id': str(item_id),
                'item_name': item.name,
                'available_quantity': item.quantity,  # Use Item.quantity directly
                'unit_of_measure': item.unit_of_measure
            }
        except Item.DoesNotExist:
            return {
                'item_id': str(item_id),
                'item_name': None,
                'available_quantity': 0,
                'unit_of_measure': None
            }
    
    @staticmethod
    def adjust_inventory(item_id, quantity, reason, reference_id=None, performed_by=None):
        """Adjust inventory by creating a transaction record"""
        # Determine transaction type based on quantity
        transaction_type = 'ADJUSTMENT'
        if 'production' in reason.lower():
            if quantity < 0:
                transaction_type = 'PRODUCTION_IN'  # Consumed in production
            else:
                transaction_type = 'PRODUCTION_OUT'  # Produced in production
                
        # Handle reference_id (store in notes since the field requires an integer)
        ref_id_str = ""
        if reference_id:
            # Store complete reference ID in notes
            ref_id_str = f" (Ref: {reference_id})"
            
        # Add performer info to notes if available
        performer_info = ""
        if performed_by:
            performer_info = f" - by {performed_by.username}"
            
        # Create inventory transaction with numerical reference_id or None
        transaction = InventoryTransaction.objects.create(
            item_id=item_id,
            quantity=quantity,  # Can be positive (addition) or negative (reduction)
            transaction_type=transaction_type,
            # Don't pass reference_id if it's not an integer
            notes=f"{reason}{ref_id_str}{performer_info}"
        )
        
        # Directly update the item quantity in the Item table
        InventoryRepository.update_item_quantity(item_id, int(quantity))
        
        return transaction
    
    @staticmethod
    def update_item_quantity(item_id, quantity_change):
        """
        Directly update the item quantity in the Item table.
        
        Args:
            item_id: UUID of the item to update
            quantity_change: Integer change in quantity (can be positive or negative)
        
        Returns:
            Updated Item instance
        """
        # Get the item
        item = Item.objects.get(id=item_id)
        
        # Update quantity
        item.quantity = item.quantity + quantity_change
        
        # Save the item
        item.save(update_fields=['quantity'])
        
        return item
    
    @staticmethod
    def get_inventory_transactions(item_id=None, date_from=None, date_to=None):
        """Get inventory transactions with optional filtering"""
        queryset = InventoryTransaction.objects.all().select_related('item', 'performed_by')
        
        if item_id:
            queryset = queryset.filter(item_id=item_id)
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_low_stock_items(threshold_percentage=20):
        """Get items that are low in stock"""
        low_stock_items = []
        
        # Get all items
        items = Item.objects.all()
        
        for item in items:
            if item.minimum_stock:
                # Calculate current quantity
                transactions = InventoryTransaction.objects.filter(item=item)
                current_quantity = transactions.aggregate(total=Sum('quantity')).get('total', 0) or 0
                
                # Check if below threshold
                if current_quantity <= (item.minimum_stock * (threshold_percentage / 100)):
                    low_stock_items.append({
                        'item_id': str(item.id),
                        'item_name': item.name,
                        'current_quantity': current_quantity,
                        'minimum_stock': item.minimum_stock,
                        'unit_of_measure': item.unit_of_measure,
                        'is_critical': current_quantity <= 0
                    })
        
        return low_stock_items
