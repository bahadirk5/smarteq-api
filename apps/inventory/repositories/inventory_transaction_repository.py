from apps.common.repositories.base_repository import BaseRepository
from apps.inventory.models import InventoryTransaction


class InventoryTransactionRepository(BaseRepository):
    """
    Repository class for inventory transaction operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(InventoryTransaction)
    
    def create_transaction(self, transaction_data):
        """
        Create a new inventory transaction.
        
        Args:
            transaction_data (dict): Data for the new transaction
            
        Returns:
            InventoryTransaction: Created transaction instance
        """
        return self.model.objects.create(**transaction_data)
    
    def get_transactions_by_item(self, item_id):
        """
        Get all transactions for a specific item.
        
        Args:
            item_id (int): ID of the item
            
        Returns:
            QuerySet: Transactions related to the specified item
        """
        return self.filter(item_id=item_id)
    
    def get_transactions_by_type(self, transaction_type):
        """
        Get all transactions of a specific type.
        
        Args:
            transaction_type (str): Type of transaction
            
        Returns:
            QuerySet: Transactions of the specified type
        """
        return self.filter(transaction_type=transaction_type)
    
    def get_transactions_by_reference(self, reference_model, reference_id):
        """
        Get transactions associated with a specific reference (e.g., a production process).
        
        Args:
            reference_model (str): Name of the model being referenced
            reference_id (int): ID of the referenced entity
            
        Returns:
            QuerySet: Transactions referencing the specified entity
        """
        return self.filter(reference_model=reference_model, reference_id=reference_id)
