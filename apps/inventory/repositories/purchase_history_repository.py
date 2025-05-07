from django.db.models import Sum, Avg, Max, F
from apps.inventory.models.purchase_history import PurchaseHistory


class PurchaseHistoryRepository:
    """
    Repository class for PurchaseHistory model
    """
    @staticmethod
    def create(item, purchase_date, quantity, unit_price, supplier=None, invoice_reference=None, notes=None):
        """
        Create a new purchase history record
        """
        return PurchaseHistory.objects.create(
            item=item,
            purchase_date=purchase_date,
            quantity=quantity,
            unit_price=unit_price,
            total_price=quantity * unit_price,
            supplier=supplier,
            invoice_reference=invoice_reference,
            notes=notes
        )
    
    @staticmethod
    def get_by_id(purchase_id):
        """
        Get purchase history by id
        """
        try:
            return PurchaseHistory.objects.get(id=purchase_id)
        except PurchaseHistory.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_item(item_id, order_by='-purchase_date'):
        """
        Get purchase history for a specific item
        """
        return PurchaseHistory.objects.filter(item_id=item_id).order_by(order_by)
    
    @staticmethod
    def get_latest_purchase_for_item(item_id):
        """
        Get the most recent purchase for an item
        """
        return PurchaseHistory.objects.filter(item_id=item_id).order_by('-purchase_date').first()
    
    @staticmethod
    def get_avg_purchase_price(item_id):
        """
        Get the average purchase price for an item
        """
        result = PurchaseHistory.objects.filter(item_id=item_id).aggregate(
            avg_price=Avg('unit_price')
        )
        return result['avg_price']
    
    @staticmethod
    def get_total_purchased_quantity(item_id):
        """
        Get the total quantity purchased for an item
        """
        result = PurchaseHistory.objects.filter(item_id=item_id).aggregate(
            total_qty=Sum('quantity')
        )
        return result['total_qty'] or 0
    
    @staticmethod
    def update(purchase_id, **kwargs):
        """
        Update a purchase history record
        """
        try:
            purchase = PurchaseHistory.objects.get(id=purchase_id)
            
            for key, value in kwargs.items():
                setattr(purchase, key, value)
            
            if 'quantity' in kwargs or 'unit_price' in kwargs:
                purchase.total_price = purchase.quantity * purchase.unit_price
            
            purchase.save()
            return purchase
        except PurchaseHistory.DoesNotExist:
            return None
    
    @staticmethod
    def delete(purchase_id):
        """
        Delete a purchase history record
        """
        try:
            purchase = PurchaseHistory.objects.get(id=purchase_id)
            purchase.delete()
            return True
        except PurchaseHistory.DoesNotExist:
            return False
