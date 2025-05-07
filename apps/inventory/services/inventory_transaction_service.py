from apps.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from apps.inventory.repositories.item_repository import ItemRepository


class InventoryTransactionService:
    """
    Service class to handle business logic for Inventory Transaction operations.
    Uses InventoryTransactionRepository for data access.
    """
    
    def __init__(self):
        self.repository = InventoryTransactionRepository()
        self.item_repository = ItemRepository()
    
    def get_all_transactions(self, **filters):
        """
        Get all inventory transactions, with optional filtering.
        
        Args:
            **filters: Optional filters to apply to the query
            
        Returns:
            QuerySet: All transactions matching the filters
        """
        return self.repository.filter(**filters)
    
    def get_transaction(self, transaction_id):
        """
        Get a specific inventory transaction by ID.
        
        Args:
            transaction_id: ID of the transaction to retrieve
            
        Returns:
            InventoryTransaction: The transaction with the specified ID
        """
        return self.repository.get(id=transaction_id)
    
    def get_transactions_by_item(self, item_id):
        """
        Get all transactions for a specific item.
        
        Args:
            item_id: ID of the item
            
        Returns:
            QuerySet: Transactions for the specified item
        """
        return self.repository.get_transactions_by_item(item_id)
    
    def get_transactions_by_reference(self, reference_model, reference_id):
        """
        Get transactions for a specific reference (e.g., a production process).
        
        Args:
            reference_model: Name of the model being referenced
            reference_id: ID of the referenced entity
            
        Returns:
            QuerySet: Transactions for the specified reference
        """
        return self.repository.get_transactions_by_reference(reference_model, reference_id)
    
    def create_transaction(self, transaction_data):
        """
        Create a new inventory transaction and update item quantity.
        
        Args:
            transaction_data: Data for the new transaction
            
        Returns:
            InventoryTransaction: The created transaction
        """
        # Get the item and update its quantity
        item_id = transaction_data.get('item')
        if isinstance(item_id, dict) and 'id' in item_id:
            item_id = item_id['id']
            
        item = self.item_repository.get(id=item_id)
        quantity = transaction_data.get('quantity', 0)
        
        # Update item quantity - positive values increase stock, negative values decrease
        item.quantity += quantity
        self.item_repository.update(item.id, {'quantity': item.quantity})
        
        # Create the transaction record
        return self.repository.create_transaction(transaction_data)
