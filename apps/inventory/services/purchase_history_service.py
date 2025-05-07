from datetime import date
from apps.inventory.repositories.purchase_history_repository import PurchaseHistoryRepository
from apps.inventory.repositories.item_repository import ItemRepository


class PurchaseHistoryService:
    """
    Service class for managing purchase history
    """
    @staticmethod
    def create_purchase_record(item_id, purchase_date, quantity, unit_price, supplier=None, invoice_reference=None, notes=None):
        """
        Create a new purchase history record and update the item's purchase price
        """
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return None, "Item not found"
        
        if not item.is_raw_material:
            return None, "Only raw materials can have purchase history"
        
        purchase = PurchaseHistoryRepository.create(
            item=item,
            purchase_date=purchase_date,
            quantity=quantity,
            unit_price=unit_price,
            supplier=supplier,
            invoice_reference=invoice_reference,
            notes=notes
        )
        
        # Update item quantity
        ItemRepository.update(item_id, quantity=item.quantity + quantity)
        
        return purchase, None
    
    @staticmethod
    def get_purchase_history(item_id, order_by='-purchase_date'):
        """
        Get purchase history for an item
        """
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return [], "Item not found"
            
        return PurchaseHistoryRepository.get_by_item(item_id, order_by=order_by), None
    
    @staticmethod
    def get_avg_purchase_price(item_id):
        """
        Get average purchase price for an item
        """
        item = ItemRepository.get_by_id(item_id)
        if not item:
            return None, "Item not found"
            
        avg_price = PurchaseHistoryRepository.get_avg_purchase_price(item_id)
        return avg_price, None
    
    @staticmethod
    def update_purchase_record(purchase_id, **kwargs):
        """
        Update a purchase history record
        """
        purchase = PurchaseHistoryRepository.get_by_id(purchase_id)
        if not purchase:
            return None, "Purchase record not found"
        
        old_quantity = purchase.quantity
        updated_purchase = PurchaseHistoryRepository.update(purchase_id, **kwargs)
        
        # Update item quantity if the purchase quantity changed
        if 'quantity' in kwargs and kwargs['quantity'] != old_quantity:
            quantity_diff = kwargs['quantity'] - old_quantity
            ItemRepository.update(
                purchase.item.id, 
                quantity=purchase.item.quantity + quantity_diff
            )
        
        return updated_purchase, None
    
    @staticmethod
    def delete_purchase_record(purchase_id):
        """
        Delete a purchase history record and update item quantity
        """
        purchase = PurchaseHistoryRepository.get_by_id(purchase_id)
        if not purchase:
            return False, "Purchase record not found"
        
        # Update item quantity to remove the purchased amount
        ItemRepository.update(
            purchase.item.id,
            quantity=max(0, purchase.item.quantity - purchase.quantity)
        )
        
        result = PurchaseHistoryRepository.delete(purchase_id)
        return result, None
