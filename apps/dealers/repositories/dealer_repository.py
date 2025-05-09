from django.db import models
from apps.dealers.models import Dealer
from apps.common.repositories.base_repository import BaseRepository


class DealerRepository(BaseRepository):
    """
    Repository for Dealer model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(Dealer)
    
    def get_by_code(self, code):
        """
        Get a dealer by code
        
        Args:
            code: Unique dealer code
            
        Returns:
            Dealer instance or None if not found
        """
        try:
            return self.model.objects.get(code=code)
        except self.model.DoesNotExist:
            return None
    
    def get_active_dealers(self):
        """
        Get all active dealers
        
        Returns:
            QuerySet of active dealers
        """
        return self.model.objects.filter(is_active=True)
    
    def search_dealers(self, query):
        """
        Search dealers by name, code, contact person or email
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of matching dealers
        """
        return self.model.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(code__icontains=query) |
            models.Q(contact_person__icontains=query) |
            models.Q(email__icontains=query)
        ).distinct()