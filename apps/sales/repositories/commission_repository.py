from django.db import models
from django.db import transaction
from apps.sales.models import OrderCommission, CommissionType
from apps.common.repositories.base_repository import BaseRepository


class OrderCommissionRepository(BaseRepository):
    """
    Repository for OrderCommission model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(OrderCommission)
    
    def get_by_order(self, order_id):
        """
        Get all commissions for a specific order
        
        Args:
            order_id: Order ID
            
        Returns:
            QuerySet of commissions
        """
        return self.model.objects.filter(order_id=order_id)
    
    def get_by_type(self, commission_type):
        """
        Get all commissions of a specific type
        
        Args:
            commission_type: Commission type
            
        Returns:
            QuerySet of commissions
        """
        return self.model.objects.filter(commission_type=commission_type)
    
    def get_collected(self):
        """
        Get all collected commissions
        
        Returns:
            QuerySet of collected commissions
        """
        return self.model.objects.filter(is_collected=True)
    
    def get_uncollected(self):
        """
        Get all uncollected commissions
        
        Returns:
            QuerySet of uncollected commissions
        """
        return self.model.objects.filter(is_collected=False)
    
    def get_by_third_party(self, third_party_name):
        """
        Get all commissions for a specific third party
        
        Args:
            third_party_name: Name of the third party
            
        Returns:
            QuerySet of commissions
        """
        return self.model.objects.filter(
            commission_type=CommissionType.THIRD_PARTY,
            third_party_name__icontains=third_party_name
        )
    
    @transaction.atomic
    def mark_as_collected(self, commission_id):
        """
        Mark a commission as collected
        
        Args:
            commission_id: Commission ID
            
        Returns:
            Updated OrderCommission instance
        """
        commission = self.get(id=commission_id)
        commission.is_collected = True
        commission.save()
        return commission
    
    @transaction.atomic
    def create_multiple(self, commissions_data):
        """
        Create multiple commission records
        
        Args:
            commissions_data: List of commission data dictionaries
            
        Returns:
            List of created OrderCommission instances
        """
        commissions = []
        for data in commissions_data:
            commission = self.model.objects.create(**data)
            commissions.append(commission)
        return commissions