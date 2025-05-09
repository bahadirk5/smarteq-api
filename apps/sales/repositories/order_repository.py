from django.db import models
from django.db import transaction
from apps.sales.models import Order, OrderItem, OrderStatus
from apps.common.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    """
    Repository for Order model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(Order)
    
    def get_by_number(self, order_number):
        """
        Get an order by its number
        
        Args:
            order_number: Order number
            
        Returns:
            Order instance or None if not found
        """
        try:
            return self.model.objects.get(order_number=order_number)
        except self.model.DoesNotExist:
            return None
    
    def get_by_dealer(self, dealer_id):
        """
        Get all orders for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of orders
        """
        return self.model.objects.filter(dealer_id=dealer_id)
    
    def get_by_status(self, status):
        """
        Get all orders with a specific status
        
        Args:
            status: Order status
            
        Returns:
            QuerySet of orders
        """
        return self.model.objects.filter(status=status)
    
    def get_paid_orders(self):
        """
        Get all paid orders
        
        Returns:
            QuerySet of paid orders
        """
        return self.model.objects.filter(is_paid=True)
    
    def get_unpaid_orders(self):
        """
        Get all unpaid orders
        
        Returns:
            QuerySet of unpaid orders
        """
        return self.model.objects.filter(is_paid=False)
    
    @transaction.atomic
    def create_order_with_items(self, order_data, items_data):
        """
        Create an order with its items
        
        Args:
            order_data: Order data
            items_data: List of order items data
            
        Returns:
            Created Order instance
        """
        # Create the order
        order = self.model.objects.create(**order_data)
        
        # Create order items
        for item_data in items_data:
            item_data['order'] = order
            OrderItem.objects.create(**item_data)
        
        # Calculate total price
        order.calculate_total_price()
        
        return order
    
    @transaction.atomic
    def update_order_status(self, order_id, status):
        """
        Update the status of an order
        
        Args:
            order_id: Order ID
            status: New status
            
        Returns:
            Updated Order instance
        """
        order = self.get(id=order_id)
        old_status = order.status
        order.status = status
        
        # If the order is being marked as delivered, set the delivery date
        if status == OrderStatus.DELIVERED and old_status != OrderStatus.DELIVERED:
            from django.utils import timezone
            order.delivery_date = timezone.now().date()
            
        # If the order is being marked as completed, set the completion date
        if status == OrderStatus.DELIVERED and old_status != OrderStatus.DELIVERED:
            from django.utils import timezone
            order.completion_date = timezone.now().date()
            
        order.save()
        return order
    
    @transaction.atomic
    def mark_as_paid(self, order_id):
        """
        Mark an order as paid
        
        Args:
            order_id: Order ID
            
        Returns:
            Updated Order instance
        """
        order = self.get(id=order_id)
        order.is_paid = True
        order.save()
        return order