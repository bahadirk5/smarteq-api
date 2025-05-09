from django.db import transaction
from apps.sales.repositories.order_item_repository import OrderItemRepository
from apps.sales.repositories.order_repository import OrderRepository
from apps.inventory.repositories.item_repository import ItemRepository


class OrderItemService:
    """
    Service class to handle business logic for OrderItem operations.
    Uses OrderItemRepository for data access.
    """
    
    def __init__(
        self,
        order_item_repository: OrderItemRepository = None,
        order_repository: OrderRepository = None,
        item_repository: ItemRepository = None
    ):
        self.repository = order_item_repository or OrderItemRepository()
        self.order_repository = order_repository or OrderRepository()
        self.item_repository = item_repository or ItemRepository()
    
    def get_all_order_items(self):
        """
        Get all order items
        
        Returns:
            QuerySet of all order items
        """
        return self.repository.list()
    
    def get_order_item(self, order_item_id):
        """
        Get an order item by ID
        
        Args:
            order_item_id: OrderItem ID
            
        Returns:
            OrderItem instance or None if not found
        """
        return self.repository.get(id=order_item_id)
    
    def get_order_items_by_order(self, order_id):
        """
        Get all order items for a specific order
        
        Args:
            order_id: Order ID
            
        Returns:
            QuerySet of order items
        """
        return self.repository.get_by_order(order_id)
    
    def get_order_items_by_product(self, product_id):
        """
        Get all order items for a specific product/item
        
        Args:
            product_id: Product/Item ID
            
        Returns:
            QuerySet of order items
        """
        return self.repository.get_by_product(product_id)
    
    @transaction.atomic
    def create_order_item(self, order_item_data):
        """
        Create a new order item
        
        Args:
            order_item_data: Dictionary with order item data
            
        Returns:
            Created OrderItem instance
            
        Raises:
            ValueError: When validation fails
        """
        # Verify order exists
        if 'order_id' in order_item_data:
            order = self.order_repository.get(id=order_item_data['order_id'])
            if not order:
                raise ValueError(f"Order with ID {order_item_data['order_id']} not found")
        
        # Verify item exists
        if 'item_id' in order_item_data:
            item = self.item_repository.get(id=order_item_data['item_id'])
            if not item:
                raise ValueError(f"Item with ID {order_item_data['item_id']} not found")
        
        # Check if order item already exists
        if 'order_id' in order_item_data and 'item_id' in order_item_data:
            existing_item = self.repository.get_by_order_and_product(
                order_item_data['order_id'], 
                order_item_data['item_id']
            )
            if existing_item:
                # Update quantity instead of creating a new item
                existing_item.quantity += order_item_data.get('quantity', 1)
                existing_item.save()
                return existing_item
        
        # Create the order item
        return self.repository.create(**order_item_data)
    
    @transaction.atomic
    def update_order_item(self, order_item_id, order_item_data):
        """
        Update an existing order item
        
        Args:
            order_item_id: OrderItem ID to update
            order_item_data: Dictionary with updated order item data
            
        Returns:
            Updated OrderItem instance
            
        Raises:
            ValueError: When validation fails
        """
        order_item = self.repository.get(id=order_item_id)
        if not order_item:
            return None
        
        # Check if quantity is being updated
        if 'quantity' in order_item_data:
            quantity = order_item_data['quantity']
            if quantity <= 0:
                # Delete the item if quantity is zero or negative
                self.repository.delete(order_item)
                return None
        
        return self.repository.update(order_item, **order_item_data)
    
    def delete_order_item(self, order_item_id):
        """
        Delete an order item
        
        Args:
            order_item_id: OrderItem ID to delete
            
        Returns:
            Boolean indicating success
        """
        order_item = self.repository.get(id=order_item_id)
        if not order_item:
            return False
        
        self.repository.delete(order_item)
        return True
    
    @transaction.atomic
    def update_quantity(self, order_item_id, quantity):
        """
        Update the quantity of an order item
        
        Args:
            order_item_id: OrderItem ID
            quantity: New quantity
            
        Returns:
            Updated OrderItem instance or None if deleted
            
        Raises:
            ValueError: When order item not found
        """
        if quantity <= 0:
            # Delete the item if quantity is zero or negative
            return self.delete_order_item(order_item_id)
        
        return self.repository.update_quantity(order_item_id, quantity)