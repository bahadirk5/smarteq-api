from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg
from apps.service.repositories.repair_request_repository import RepairRequestRepository
from apps.sales.repositories.device_repository import DeviceRepository
from apps.sales.services.device_service import DeviceService
from apps.service.models import RepairStatus


class RepairRequestService:
    """
    Service class to handle business logic for Repair Request operations.
    Uses RepairRequestRepository for data access.
    """
    
    def __init__(
        self,
        repair_request_repository: RepairRequestRepository = None,
        device_repository: DeviceRepository = None,
        device_service: DeviceService = None
    ):
        self.repository = repair_request_repository or RepairRequestRepository()
        self.device_repository = device_repository or DeviceRepository()
        self.device_service = device_service or DeviceService()
    
    def get_all_repair_requests(self):
        """
        Get all repair requests
        
        Returns:
            QuerySet of all repair requests
        """
        return self.repository.list()
    
    def get_repair_request(self, repair_id):
        """
        Get a repair request by ID
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            RepairRequest instance or None if not found
        """
        return self.repository.get(id=repair_id)
    
    def get_repair_request_by_number(self, repair_number):
        """
        Get a repair request by its repair number
        
        Args:
            repair_number: Repair number
            
        Returns:
            RepairRequest instance or None if not found
        """
        return self.repository.get_by_number(repair_number)
    
    def get_repair_requests_by_device(self, device_id):
        """
        Get all repair requests for a specific device
        
        Args:
            device_id: Device ID
            
        Returns:
            QuerySet of repair requests or None if device not found
        """
        # Verify device exists
        device = self.device_repository.get(id=device_id)
        if not device:
            return None
            
        return self.repository.get_by_device(device_id)
    
    def get_repair_requests_by_status(self, status):
        """
        Get all repair requests with a specific status
        
        Args:
            status: Repair status
            
        Returns:
            QuerySet of repair requests
        """
        return self.repository.get_by_status(status)
    
    def get_warranty_repairs(self):
        """
        Get all warranty repair requests
        
        Returns:
            QuerySet of warranty repair requests
        """
        return self.repository.get_warranty_repairs()
    
    def get_non_warranty_repairs(self):
        """
        Get all non-warranty repair requests
        
        Returns:
            QuerySet of non-warranty repair requests
        """
        return self.repository.get_non_warranty_repairs()
    
    def get_repair_statistics(self, start_date=None, end_date=None):
        """
        Get repair request statistics
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Dictionary with repair statistics
        """
        if not start_date:
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = timezone.now()
            
        repairs = self.repository.get_by_date_range(start_date, end_date)
        
        statistics = {
            'total': repairs.count(),
            'warranty': repairs.filter(is_warranty=True).count(),
            'non_warranty': repairs.filter(is_warranty=False).count(),
            'pending': repairs.filter(status=RepairStatus.PENDING).count(),
            'in_progress': repairs.filter(status=RepairStatus.IN_PROGRESS).count(),
            'completed': repairs.filter(status=RepairStatus.COMPLETED).count(),
            'cancelled': repairs.filter(status=RepairStatus.CANCELLED).count(),
            'avg_repair_cost': repairs.exclude(repair_cost=0).aggregate(Avg('repair_cost'))['repair_cost__avg'] or 0,
        }
        
        return statistics
    
    @transaction.atomic
    def create_repair_request(self, repair_data, parts_data=None):
        """
        Create a new repair request with optional parts
        
        Args:
            repair_data: Dictionary with repair request data
            parts_data: List of dictionaries with repair part data (optional)
            
        Returns:
            Created RepairRequest instance
            
        Raises:
            ValueError: When validation fails
        """
        # Validate device exists
        if 'device_id' in repair_data:
            device = self.device_repository.get(id=repair_data['device_id'])
            if not device:
                raise ValueError(f"Device with ID {repair_data['device_id']} not found")
        
        # Generate repair number if not provided
        if 'repair_number' not in repair_data:
            today = timezone.now()
            prefix = 'REP'
            repair_data['repair_number'] = f"{prefix}-{today.strftime('%Y%m%d')}-{today.timestamp():.0f}"
        
        # Determine warranty status if not provided
        if 'is_warranty' not in repair_data and 'device_id' in repair_data:
            warranty_info = self.device_service.check_warranty_status(repair_data['device_id'])
            repair_data['is_warranty'] = warranty_info.get('in_warranty', False) if warranty_info else False
        
        # Set initial status if not provided
        if 'status' not in repair_data:
            repair_data['status'] = RepairStatus.PENDING
        
        # Create repair request with parts if provided
        if parts_data:
            return self.repository.create_with_parts(repair_data, parts_data)
        else:
            return self.repository.create(**repair_data)
    
    @transaction.atomic
    def update_repair_status(self, repair_id, status, notes=None):
        """
        Update the status of a repair request
        
        Args:
            repair_id: Repair request ID
            status: New repair status
            notes: Optional status update notes
            
        Returns:
            Updated RepairRequest instance
            
        Raises:
            ValueError: When repair not found or status invalid
        """
        if status not in [choice[0] for choice in RepairStatus.choices]:
            raise ValueError(f"Invalid repair status: {status}")
        
        repair = self.repository.get(id=repair_id)
        if not repair:
            raise ValueError(f"Repair request with ID {repair_id} not found")
        
        status_notes = None
        if notes:
            status_notes = f"{timezone.now().strftime('%Y-%m-%d %H:%M')} - {status}: {notes}"
            
        return self.repository.update_status(repair_id, status, status_notes)
    
    @transaction.atomic
    def set_repair_cost(self, repair_id, repair_cost):
        """
        Set the repair cost for a repair request
        
        Args:
            repair_id: Repair request ID
            repair_cost: Repair cost amount
            
        Returns:
            Updated RepairRequest instance
            
        Raises:
            ValueError: When repair not found
        """
        repair = self.repository.get(id=repair_id)
        if not repair:
            raise ValueError(f"Repair request with ID {repair_id} not found")
            
        return self.repository.set_repair_cost(repair_id, repair_cost)
    
    def delete_repair_request(self, repair_id):
        """
        Delete a repair request
        
        Args:
            repair_id: Repair request ID
            
        Returns:
            Boolean indicating success
            
        Raises:
            ValueError: When repair request cannot be deleted
        """
        repair = self.repository.get(id=repair_id)
        if not repair:
            return False
        
        # Repairs that are in progress or completed cannot be deleted
        if repair.status in [RepairStatus.IN_PROGRESS, RepairStatus.COMPLETED]:
            raise ValueError(f"Cannot delete repair request with status {repair.status}")
            
        return self.repository.delete(repair)