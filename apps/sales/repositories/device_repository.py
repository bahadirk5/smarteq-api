from django.db import models
from datetime import date
from apps.sales.models import Device
from apps.common.repositories.base_repository import BaseRepository


class DeviceRepository(BaseRepository):
    """
    Repository for Device model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(Device)
    
    def get_by_serial_number(self, serial_number):
        """
        Get a device by serial number
        
        Args:
            serial_number: Device serial number
            
        Returns:
            Device instance or None if not found
        """
        try:
            return self.model.objects.get(serial_number=serial_number)
        except self.model.DoesNotExist:
            return None
    
    def get_by_item(self, item_id):
        """
        Get all devices of a specific item type
        
        Args:
            item_id: Item ID
            
        Returns:
            QuerySet of devices
        """
        return self.model.objects.filter(item_id=item_id)
    
    def get_in_warranty(self):
        """
        Get all devices that are currently in warranty
        
        Returns:
            QuerySet of devices in warranty
        """
        today = date.today()
        return self.model.objects.filter(
            models.Q(purchase_date__isnull=False) & 
            models.Q(purchase_date__add=models.F('warranty_period_months') * 30, gt=today)
        )
    
    def get_out_of_warranty(self):
        """
        Get all devices that are out of warranty
        
        Returns:
            QuerySet of devices out of warranty
        """
        today = date.today()
        return self.model.objects.filter(
            models.Q(purchase_date__isnull=False) & 
            models.Q(purchase_date__add=models.F('warranty_period_months') * 30, lte=today)
        )