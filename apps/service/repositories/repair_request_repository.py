from django.db import models
from django.db import transaction
from apps.service.models import RepairRequest, RepairStatus
from apps.common.repositories.base_repository import BaseRepository


class RepairRequestRepository(BaseRepository):
    """
    Repository for RepairRequest model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(RepairRequest)
    
    def get_by_device(self, device_id):
        """
        Get all repair requests for a specific device
        
        Args:
            device_id: Device ID
            
        Returns:
            QuerySet of repair requests
        """
        return self.model.objects.filter(device_id=device_id)
    
    def get_by_dealer(self, dealer_id):
        """
        Get all repair requests for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of repair requests
        """
        return self.model.objects.filter(dealer_id=dealer_id)
    
    def get_by_customer(self, customer_id):
        """
        Get all repair requests for a specific customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            QuerySet of repair requests
        """
        return self.model.objects.filter(customer_id=customer_id)
    
    def get_by_status(self, status):
        """
        Get all repair requests with a specific status
        
        Args:
            status: Repair request status
            
        Returns:
            QuerySet of repair requests
        """
        return self.model.objects.filter(status=status)
    
    def get_warranty_repairs(self):
        """
        Get all warranty repair requests
        
        Returns:
            QuerySet of warranty repair requests
        """
        return self.model.objects.filter(is_warranty=True)
    
    def get_non_warranty_repairs(self):
        """
        Get all non-warranty repair requests
        
        Returns:
            QuerySet of non-warranty repair requests
        """
        return self.model.objects.filter(is_warranty=False)
    
    @transaction.atomic
    def update_status(self, repair_id, status, technician_notes=None):
        """
        Update the status of a repair request
        
        Args:
            repair_id: Repair request ID
            status: New status
            technician_notes: Optional technician notes
            
        Returns:
            Updated RepairRequest instance
        """
        repair = self.get(id=repair_id)
        repair.status = status
        
        if technician_notes:
            repair.technician_notes = technician_notes
        
        # If repair is marked as completed, set completion date
        if status == RepairStatus.READY_FOR_DELIVERY:
            from django.utils import timezone
            repair.completion_date = timezone.now().date()
        
        repair.save()
        return repair
    
    @transaction.atomic
    def set_repair_cost(self, repair_id, repair_cost):
        """
        Set the repair cost for a non-warranty repair
        
        Args:
            repair_id: Repair request ID
            repair_cost: Repair cost
            
        Returns:
            Updated RepairRequest instance
        """
        repair = self.get(id=repair_id)
        repair.repair_cost = repair_cost
        repair.save()
        return repair