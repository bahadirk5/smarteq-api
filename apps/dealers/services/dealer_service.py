from apps.dealers.repositories.dealer_repository import DealerRepository


class DealerService:
    """
    Service class to handle business logic for Dealer operations.
    Uses DealerRepository for data access.
    """
    
    def __init__(self, dealer_repository: DealerRepository = None):
        self.repository = dealer_repository or DealerRepository()
    
    def get_all_dealers(self):
        """
        Get all dealers
        
        Returns:
            QuerySet of all dealers
        """
        return self.repository.list()
    
    def get_dealer(self, dealer_id):
        """
        Get a dealer by ID
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            Dealer instance or None if not found
        """
        return self.repository.get(id=dealer_id)
    
    def get_dealer_by_code(self, code):
        """
        Get a dealer by code
        
        Args:
            code: Dealer code
            
        Returns:
            Dealer instance or None if not found
        """
        return self.repository.get_by_code(code)
    
    def get_active_dealers(self):
        """
        Get all active dealers
        
        Returns:
            QuerySet of active dealers
        """
        return self.repository.get_active_dealers()
    
    def search_dealers(self, query):
        """
        Search dealers by name, code, contact person or email
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of matching dealers
        """
        return self.repository.search_dealers(query)
    
    def create_dealer(self, dealer_data):
        """
        Create a new dealer
        
        Args:
            dealer_data: Dictionary with dealer data
            
        Returns:
            Created Dealer instance
        """
        return self.repository.create(**dealer_data)
    
    def update_dealer(self, dealer_id, dealer_data):
        """
        Update an existing dealer
        
        Args:
            dealer_id: Dealer ID to update
            dealer_data: Dictionary with updated dealer data
            
        Returns:
            Updated Dealer instance
        """
        dealer = self.repository.get(id=dealer_id)
        if not dealer:
            return None
        
        return self.repository.update(dealer, **dealer_data)
    
    def delete_dealer(self, dealer_id):
        """
        Delete a dealer
        
        Args:
            dealer_id: Dealer ID to delete
            
        Returns:
            Boolean indicating success
        """
        dealer = self.repository.get(id=dealer_id)
        if not dealer:
            return False
        
        return self.repository.delete(dealer)
    
    def toggle_dealer_status(self, dealer_id):
        """
        Toggle dealer's active status
        
        Args:
            dealer_id: Dealer ID to toggle
            
        Returns:
            Updated Dealer instance or None if not found
        """
        dealer = self.repository.get(id=dealer_id)
        if not dealer:
            return None
        
        dealer.is_active = not dealer.is_active
        return self.repository.update(dealer)
    
    def activate_dealer(self, dealer_id):
        """
        Activate a dealer
        
        Args:
            dealer_id: Dealer ID to activate
            
        Returns:
            Updated Dealer instance or None if not found
        """
        dealer = self.repository.get(id=dealer_id)
        if not dealer:
            return None
            
        if dealer.is_active:
            return dealer  # Already active
            
        dealer.is_active = True
        return self.repository.update(dealer)
    
    def deactivate_dealer(self, dealer_id):
        """
        Deactivate a dealer
        
        Args:
            dealer_id: Dealer ID to deactivate
            
        Returns:
            Updated Dealer instance or None if not found
        """
        dealer = self.repository.get(id=dealer_id)
        if not dealer:
            return None
            
        if not dealer.is_active:
            return dealer  # Already inactive
            
        dealer.is_active = False
        return self.repository.update(dealer)
    
    def get_dealer_customers(self, dealer_id):
        """
        Get all customers associated with a dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of customers
        """
        from apps.customers.repositories.customer_repository import CustomerRepository
        customer_repo = CustomerRepository()
        return customer_repo.get_by_dealer(dealer_id)