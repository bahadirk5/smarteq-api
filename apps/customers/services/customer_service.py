from apps.customers.repositories.customer_repository import CustomerRepository
from apps.dealers.repositories.dealer_repository import DealerRepository


class CustomerService:
    """
    Service class to handle business logic for Customer operations.
    Uses CustomerRepository for data access.
    """
    
    def __init__(
        self,
        customer_repository: CustomerRepository = None,
        dealer_repository: DealerRepository = None
    ):
        self.repository = customer_repository or CustomerRepository()
        self.dealer_repository = dealer_repository or DealerRepository()
    
    def get_all_customers(self):
        """
        Get all customers
        
        Returns:
            QuerySet of all customers
        """
        return self.repository.list()
    
    def get_customer(self, customer_id):
        """
        Get a customer by ID
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer instance or None if not found
        """
        return self.repository.get(id=customer_id)
    
    def get_customers_by_dealer(self, dealer_id):
        """
        Get all customers for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of customers or None if dealer not found
        """
        # Verify dealer exists
        dealer = self.dealer_repository.get(id=dealer_id)
        if not dealer:
            return None
            
        return self.repository.get_by_dealer(dealer_id)
    
    def get_customers_by_type(self, customer_type):
        """
        Get customers by type (corporate or individual)
        
        Args:
            customer_type: Type of customer ('corporate' or 'individual')
            
        Returns:
            QuerySet of customers of the specified type
        """
        customer_type = customer_type.lower()
        if customer_type == 'corporate':
            return self.get_corporate_customers()
        elif customer_type == 'individual':
            return self.get_individual_customers()
        else:
            # Return empty queryset if invalid type
            return self.repository.model.objects.none()
    
    def get_corporate_customers(self):
        """
        Get all corporate customers
        
        Returns:
            QuerySet of corporate customers
        """
        return self.repository.get_corporate_customers()
    
    def get_individual_customers(self):
        """
        Get all individual customers
        
        Returns:
            QuerySet of individual customers
        """
        return self.repository.get_individual_customers()
    
    def search_customers(self, query):
        """
        Search customers by name, contact person, email or phone
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of matching customers
        """
        return self.repository.search_customers(query)
    
    def create_customer(self, customer_data):
        """
        Create a new customer
        
        Args:
            customer_data: Dictionary with customer data
            
        Returns:
            Created Customer instance
        """
        # Check if dealer exists when dealer_id is provided
        if 'dealer_id' in customer_data:
            dealer = self.dealer_repository.get(id=customer_data['dealer_id'])
            if not dealer:
                raise ValueError(f"Dealer with ID {customer_data['dealer_id']} not found")
                
        return self.repository.create(**customer_data)
    
    def update_customer(self, customer_id, customer_data):
        """
        Update an existing customer
        
        Args:
            customer_id: Customer ID to update
            customer_data: Dictionary with updated customer data
            
        Returns:
            Updated Customer instance
        """
        customer = self.repository.get(id=customer_id)
        if not customer:
            return None
            
        # Check if dealer exists when dealer_id is provided
        if 'dealer_id' in customer_data:
            dealer = self.dealer_repository.get(id=customer_data['dealer_id'])
            if not dealer:
                raise ValueError(f"Dealer with ID {customer_data['dealer_id']} not found")
                
        return self.repository.update(customer, **customer_data)
    
    def delete_customer(self, customer_id):
        """
        Delete a customer
        
        Args:
            customer_id: Customer ID to delete
            
        Returns:
            Boolean indicating success
        """
        customer = self.repository.get(id=customer_id)
        if not customer:
            return False
            
        return self.repository.delete(customer)
    
    def assign_to_dealer(self, customer_id, dealer_id):
        """
        Assign a customer to a dealer
        
        Args:
            customer_id: Customer ID to assign
            dealer_id: Dealer ID to assign to
            
        Returns:
            Updated Customer instance or None if not found
        """
        customer = self.repository.get(id=customer_id)
        if not customer:
            return None
            
        dealer = self.dealer_repository.get(id=dealer_id)
        if not dealer:
            raise ValueError(f"Dealer with ID {dealer_id} not found")
            
        return self.repository.update(customer, dealer=dealer)
        
    def get_customer_devices(self, customer_id):
        """
        Get all devices owned by a customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            QuerySet of devices
        """
        from apps.sales.repositories.device_repository import DeviceRepository
        device_repo = DeviceRepository()
        return device_repo.get_by_customer(customer_id)
        
    def get_customer_orders(self, customer_id):
        """
        Get all orders placed by a customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            QuerySet of orders
        """
        from apps.sales.repositories.order_repository import OrderRepository
        order_repo = OrderRepository()
        return order_repo.get_by_customer(customer_id)