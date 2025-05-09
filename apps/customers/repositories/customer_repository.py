from django.db import models
from apps.customers.models import Customer, CustomerType
from apps.common.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository):
    """
    Repository for Customer model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(Customer)
    
    def get_by_dealer(self, dealer_id):
        """
        Get all customers for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of customers
        """
        return self.model.objects.filter(dealer_id=dealer_id)
    
    def get_by_type(self, customer_type):
        """
        Get all customers of a specific type
        
        Args:
            customer_type: Customer type (individual or corporate)
            
        Returns:
            QuerySet of customers
        """
        return self.model.objects.filter(customer_type=customer_type)
    
    def get_corporate_customers(self):
        """
        Get all corporate customers
        
        Returns:
            QuerySet of corporate customers
        """
        return self.model.objects.filter(customer_type=CustomerType.CORPORATE)
    
    def get_individual_customers(self):
        """
        Get all individual customers
        
        Returns:
            QuerySet of individual customers
        """
        return self.model.objects.filter(customer_type=CustomerType.INDIVIDUAL)
    
    def search_customers(self, query):
        """
        Search customers by name, contact person, email or phone
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of matching customers
        """
        return self.model.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(contact_person__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(phone__icontains=query)
        ).distinct()