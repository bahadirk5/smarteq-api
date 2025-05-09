from django.db import transaction
from django.utils import timezone
from apps.sales.repositories.commission_repository import OrderCommissionRepository
from apps.sales.repositories.order_repository import OrderRepository


class OrderCommissionService:
    """
    Service class to handle business logic for Order Commission operations.
    Uses OrderCommissionRepository for data access.
    """
    
    def __init__(
        self,
        commission_repository: OrderCommissionRepository = None,
        order_repository: OrderRepository = None
    ):
        self.repository = commission_repository or OrderCommissionRepository()
        self.order_repository = order_repository or OrderRepository()
    
    def get_all_commissions(self):
        """
        Get all commission records
        
        Returns:
            QuerySet of all commission records
        """
        return self.repository.list()
    
    def get_commission(self, commission_id):
        """
        Get a commission by ID
        
        Args:
            commission_id: Commission ID
            
        Returns:
            OrderCommission instance or None if not found
        """
        return self.repository.get(id=commission_id)
    
    def get_commissions_by_order(self, order_id):
        """
        Get all commissions for a specific order
        
        Args:
            order_id: Order ID
            
        Returns:
            QuerySet of commissions
        """
        order = self.order_repository.get(id=order_id)
        if not order:
            return None
            
        return self.repository.get_by_order(order_id)
    
    def get_commissions_by_type(self, commission_type):
        """
        Get all commissions of a specific type
        
        Args:
            commission_type: Commission type
            
        Returns:
            QuerySet of commissions
        """
        return self.repository.get_by_type(commission_type)
    
    def get_collected_commissions(self):
        """
        Get all collected commissions
        
        Returns:
            QuerySet of collected commissions
        """
        return self.repository.get_collected()
    
    def get_uncollected_commissions(self):
        """
        Get all uncollected commissions
        
        Returns:
            QuerySet of uncollected commissions
        """
        return self.repository.get_uncollected()
    
    def get_commissions_by_third_party(self, third_party_name):
        """
        Get all commissions for a specific third party
        
        Args:
            third_party_name: Name of the third party
            
        Returns:
            QuerySet of commissions
        """
        return self.repository.get_by_third_party(third_party_name)
    
    @transaction.atomic
    def create_commission(self, commission_data):
        """
        Create a new commission record
        
        Args:
            commission_data: Dictionary with commission data
            
        Returns:
            Created OrderCommission instance
            
        Raises:
            ValueError: When validation fails
        """
        # Validate order exists
        if 'order_id' in commission_data:
            order = self.order_repository.get(id=commission_data['order_id'])
            if not order:
                raise ValueError(f"Order with ID {commission_data['order_id']} not found")
        
        return self.repository.create(**commission_data)
    
    @transaction.atomic
    def create_multiple_commissions(self, commissions_data):
        """
        Create multiple commission records at once
        
        Args:
            commissions_data: List of dictionaries with commission data
            
        Returns:
            List of created OrderCommission instances
            
        Raises:
            ValueError: When validation fails
        """
        # Validate all orders exist
        for comm_data in commissions_data:
            if 'order_id' in comm_data:
                order = self.order_repository.get(id=comm_data['order_id'])
                if not order:
                    raise ValueError(f"Order with ID {comm_data['order_id']} not found")
        
        return self.repository.create_multiple(commissions_data)
    
    @transaction.atomic
    def mark_as_collected(self, commission_id):
        """
        Mark a commission as collected
        
        Args:
            commission_id: Commission ID
            
        Returns:
            Updated OrderCommission instance
            
        Raises:
            ValueError: When commission not found
        """
        commission = self.repository.get(id=commission_id)
        if not commission:
            raise ValueError(f"Commission with ID {commission_id} not found")
            
        return self.repository.mark_as_collected(commission_id)
    
    def update_commission(self, commission_id, commission_data):
        """
        Update an existing commission
        
        Args:
            commission_id: Commission ID to update
            commission_data: Dictionary with updated commission data
            
        Returns:
            Updated OrderCommission instance
            
        Raises:
            ValueError: When validation fails
        """
        commission = self.repository.get(id=commission_id)
        if not commission:
            return None
            
        # Validate order exists if changing
        if 'order_id' in commission_data:
            order = self.order_repository.get(id=commission_data['order_id'])
            if not order:
                raise ValueError(f"Order with ID {commission_data['order_id']} not found")
                
        return self.repository.update(commission, **commission_data)
    
    def delete_commission(self, commission_id):
        """
        Delete a commission
        
        Args:
            commission_id: Commission ID to delete
            
        Returns:
            Boolean indicating success
        """
        commission = self.repository.get(id=commission_id)
        if not commission:
            return False
            
        return self.repository.delete(commission)