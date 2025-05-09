from django.db import models
from apps.sales.models.order import OrderItem
from apps.common.repositories.base_repository import BaseRepository


class OrderItemRepository(BaseRepository):
    """
    Repository for OrderItem model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(OrderItem)
    
    def get_by_order(self, order_id):
        """
        Get all order items for a specific order
        
        Args:
            order_id: Order ID
            
        Returns:
            QuerySet of order items
        """
        return self.model.objects.filter(order_id=order_id)
    
    def get_by_product(self, product_id):
        """
        Get all order items for a specific product/item
        
        Args:
            product_id: Product/Item ID
            
        Returns:
            QuerySet of order items
        """
        return self.model.objects.filter(item_id=product_id)
    
    def get_by_order_and_product(self, order_id, product_id):
        """
        Get an order item by order ID and product ID
        
        Args:
            order_id: Order ID
            product_id: Product/Item ID
            
        Returns:
            OrderItem instance or None if not found
        """
        try:
            return self.model.objects.get(order_id=order_id, item_id=product_id)
        except self.model.DoesNotExist:
            return None
    
    def update_quantity(self, order_item_id, quantity):
        """
        Update the quantity of an order item
        
        Args:
            order_item_id: OrderItem ID
            quantity: New quantity
            
        Returns:
            Updated OrderItem instance
        """
        order_item = self.get(id=order_item_id)
        if not order_item:
            return None
            
        if quantity <= 0:
            # Delete the item if quantity is zero or negative
            order_item.delete()
            return None
            
        order_item.quantity = quantity
        order_item.save()
        return order_item