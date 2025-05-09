from datetime import datetime
from django.db import transaction
from django.utils import timezone
from apps.sales.repositories.order_repository import OrderRepository
from apps.dealers.repositories.dealer_repository import DealerRepository
from apps.inventory.repositories.item_repository import ItemRepository
from apps.sales.models import OrderStatus


class OrderService:
    """
    Service class to handle business logic for Order operations.
    Uses OrderRepository for data access.
    """
    
    def __init__(
        self,
        order_repository: OrderRepository = None,
        dealer_repository: DealerRepository = None,
        item_repository: ItemRepository = None
    ):
        self.repository = order_repository or OrderRepository()
        self.dealer_repository = dealer_repository or DealerRepository()
        self.item_repository = item_repository or ItemRepository()
    
    def get_all_orders(self):
        """
        Get all orders
        
        Returns:
            QuerySet of all orders
        """
        return self.repository.list()
    
    def get_order(self, order_id):
        """
        Get an order by ID
        
        Args:
            order_id: Order ID
            
        Returns:
            Order instance or None if not found
        """
        return self.repository.get(id=order_id)
    
    def get_order_by_number(self, order_number):
        """
        Get an order by its order number
        
        Args:
            order_number: Order number
            
        Returns:
            Order instance or None if not found
        """
        return self.repository.get_by_number(order_number)
    
    def get_orders_by_dealer(self, dealer_id):
        """
        Get all orders for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of orders
        """
        dealer = self.dealer_repository.get(id=dealer_id)
        if not dealer:
            return None
            
        return self.repository.get_by_dealer(dealer_id)
    
    def get_orders_by_status(self, status):
        """
        Get all orders with a specific status
        
        Args:
            status: Order status
            
        Returns:
            QuerySet of orders
        """
        return self.repository.get_by_status(status)
    
    def get_paid_orders(self):
        """
        Get all paid orders
        
        Returns:
            QuerySet of paid orders
        """
        return self.repository.get_paid_orders()
    
    def get_unpaid_orders(self):
        """
        Get all unpaid orders
        
        Returns:
            QuerySet of unpaid orders
        """
        return self.repository.get_unpaid_orders()
    
    @transaction.atomic
    def create_order(self, order_data, order_items):
        """
        Create a new order with items
        
        Args:
            order_data: Dictionary with order data
            order_items: List of dictionaries with order item data
            
        Returns:
            Created Order instance
            
        Raises:
            ValueError: When validation fails
        """
        # Validate dealer exists
        if 'dealer_id' in order_data:
            dealer = self.dealer_repository.get(id=order_data['dealer_id'])
            if not dealer:
                raise ValueError(f"Dealer with ID {order_data['dealer_id']} not found")
        
        # Generate order number if not provided
        if 'order_number' not in order_data:
            today = timezone.now()
            prefix = 'ORD'
            order_data['order_number'] = f"{prefix}-{today.strftime('%Y%m%d')}-{today.timestamp():.0f}"
        
        # Validate order items
        for item in order_items:
            if 'item_id' not in item or not self.item_repository.get(id=item['item_id']):
                raise ValueError(f"Invalid item_id: {item.get('item_id')}")
        
        # Create order with items
        return self.repository.create_order_with_items(order_data, order_items)
    
    @transaction.atomic
    def update_order_status(self, order_id, status):
        """
        Update the status of an order
        
        Args:
            order_id: Order ID
            status: New order status
            
        Returns:
            Updated Order instance
            
        Raises:
            ValueError: When order not found or status invalid
        """
        if status not in [choice[0] for choice in OrderStatus.choices]:
            raise ValueError(f"Invalid order status: {status}")
        
        order = self.repository.get(id=order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
            
        return self.repository.update_order_status(order_id, status)
    
    @transaction.atomic
    def mark_as_paid(self, order_id):
        """
        Mark an order as paid
        
        Args:
            order_id: Order ID
            
        Returns:
            Updated Order instance
            
        Raises:
            ValueError: When order not found
        """
        order = self.repository.get(id=order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
            
        return self.repository.mark_as_paid(order_id)
    
    def delete_order(self, order_id):
        """
        Delete an order
        
        Args:
            order_id: Order ID
            
        Returns:
            Boolean indicating success
            
        Raises:
            ValueError: When order cannot be deleted
        """
        order = self.repository.get(id=order_id)
        if not order:
            return False
            
        # Orders that are not in pending status cannot be deleted
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot delete order with status {order.status}")
            
        return self.repository.delete(order)