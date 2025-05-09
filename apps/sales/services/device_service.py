from datetime import date, timedelta
from django.db import transaction
from apps.sales.repositories.device_repository import DeviceRepository
from apps.inventory.repositories.item_repository import ItemRepository


class DeviceService:
    """
    Service class to handle business logic for Device operations.
    Uses DeviceRepository for data access.
    """
    
    def __init__(
        self,
        device_repository: DeviceRepository = None,
        item_repository: ItemRepository = None
    ):
        self.repository = device_repository or DeviceRepository()
        self.item_repository = item_repository or ItemRepository()
    
    def get_all_devices(self):
        """
        Get all devices
        
        Returns:
            QuerySet of all devices
        """
        return self.repository.list()
    
    def get_device(self, device_id):
        """
        Get a device by ID
        
        Args:
            device_id: Device ID
            
        Returns:
            Device instance or None if not found
        """
        return self.repository.get(id=device_id)
    
    def get_device_by_serial_number(self, serial_number):
        """
        Get a device by its serial number
        
        Args:
            serial_number: Device serial number
            
        Returns:
            Device instance or None if not found
        """
        return self.repository.get_by_serial_number(serial_number)
    
    def get_devices_by_item(self, item_id):
        """
        Get all devices of a specific item type
        
        Args:
            item_id: Item ID
            
        Returns:
            QuerySet of devices
        """
        # Validate item exists
        item = self.item_repository.get(id=item_id)
        if not item:
            return None
            
        return self.repository.get_by_item(item_id)
    
    def get_devices_in_warranty(self):
        """
        Get all devices that are currently in warranty
        
        Returns:
            QuerySet of devices in warranty
        """
        return self.repository.get_in_warranty()
    
    def get_devices_out_of_warranty(self):
        """
        Get all devices that are out of warranty
        
        Returns:
            QuerySet of devices out of warranty
        """
        return self.repository.get_out_of_warranty()
    
    def check_warranty_status(self, device_id):
        """
        Check the warranty status of a device
        
        Args:
            device_id: Device ID
            
        Returns:
            Dictionary with warranty status information
        """
        device = self.repository.get(id=device_id)
        if not device:
            return None
            
        today = date.today()
        
        if not device.purchase_date or not device.warranty_period_months:
            return {
                'device': device,
                'in_warranty': False,
                'warranty_status': 'No warranty information available'
            }
            
        # Calculate warranty end date
        days_in_month = 30  # Average days in a month for warranty purposes
        warranty_days = device.warranty_period_months * days_in_month
        warranty_end_date = device.purchase_date + timedelta(days=warranty_days)
        days_left = (warranty_end_date - today).days
        
        return {
            'device': device,
            'in_warranty': today <= warranty_end_date,
            'warranty_end_date': warranty_end_date,
            'days_left': max(0, days_left),
            'warranty_status': 'Active' if today <= warranty_end_date else 'Expired'
        }
    
    @transaction.atomic
    def create_device(self, device_data):
        """
        Create a new device
        
        Args:
            device_data: Dictionary with device data
            
        Returns:
            Created Device instance
            
        Raises:
            ValueError: When validation fails
        """
        # Validate item exists
        if 'item_id' in device_data:
            item = self.item_repository.get(id=device_data['item_id'])
            if not item:
                raise ValueError(f"Item with ID {device_data['item_id']} not found")
        
        # Check for duplicate serial number
        if 'serial_number' in device_data:
            existing = self.repository.get_by_serial_number(device_data['serial_number'])
            if existing:
                raise ValueError(f"Device with serial number {device_data['serial_number']} already exists")
                
        return self.repository.create(**device_data)
    
    @transaction.atomic
    def update_device(self, device_id, device_data):
        """
        Update an existing device
        
        Args:
            device_id: Device ID to update
            device_data: Dictionary with updated device data
            
        Returns:
            Updated Device instance
            
        Raises:
            ValueError: When validation fails
        """
        device = self.repository.get(id=device_id)
        if not device:
            return None
            
        # Validate item exists if changing
        if 'item_id' in device_data:
            item = self.item_repository.get(id=device_data['item_id'])
            if not item:
                raise ValueError(f"Item with ID {device_data['item_id']} not found")
        
        # Check for duplicate serial number if changing
        if 'serial_number' in device_data and device_data['serial_number'] != device.serial_number:
            existing = self.repository.get_by_serial_number(device_data['serial_number'])
            if existing:
                raise ValueError(f"Device with serial number {device_data['serial_number']} already exists")
                
        return self.repository.update(device, **device_data)
    
    def delete_device(self, device_id):
        """
        Delete a device
        
        Args:
            device_id: Device ID to delete
            
        Returns:
            Boolean indicating success
        """
        device = self.repository.get(id=device_id)
        if not device:
            return False
            
        return self.repository.delete(device)