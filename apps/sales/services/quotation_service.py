from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from apps.sales.repositories.quotation_repository import QuotationRepository
from apps.dealers.repositories.dealer_repository import DealerRepository
from apps.inventory.repositories.item_repository import ItemRepository
from apps.sales.models import QuotationStatus


class QuotationService:
    """
    Service class to handle business logic for Quotation operations.
    Uses QuotationRepository for data access.
    """
    
    def __init__(
        self,
        quotation_repository: QuotationRepository = None,
        dealer_repository: DealerRepository = None,
        item_repository: ItemRepository = None
    ):
        self.repository = quotation_repository or QuotationRepository()
        self.dealer_repository = dealer_repository or DealerRepository()
        self.item_repository = item_repository or ItemRepository()
    
    def get_all_quotations(self):
        """
        Get all quotations
        
        Returns:
            QuerySet of all quotations
        """
        return self.repository.list()
    
    def get_quotation(self, quotation_id):
        """
        Get a quotation by ID
        
        Args:
            quotation_id: Quotation ID
            
        Returns:
            Quotation instance or None if not found
        """
        return self.repository.get(id=quotation_id)
    
    def get_quotation_by_number(self, quotation_number):
        """
        Get a quotation by its quotation number
        
        Args:
            quotation_number: Quotation number
            
        Returns:
            Quotation instance or None if not found
        """
        return self.repository.get_by_number(quotation_number)
    
    def get_quotations_by_dealer(self, dealer_id):
        """
        Get all quotations for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of quotations
        """
        dealer = self.dealer_repository.get(id=dealer_id)
        if not dealer:
            return None
            
        return self.repository.get_by_dealer(dealer_id)
    
    def get_quotations_by_status(self, status):
        """
        Get all quotations with a specific status
        
        Args:
            status: Quotation status
            
        Returns:
            QuerySet of quotations
        """
        return self.repository.get_by_status(status)
    
    def get_valid_quotations(self):
        """
        Get all valid quotations (not expired)
        
        Returns:
            QuerySet of valid quotations
        """
        return self.repository.get_valid_quotations()
    
    def get_expired_quotations(self):
        """
        Get all expired quotations
        
        Returns:
            QuerySet of expired quotations
        """
        return self.repository.get_expired_quotations()
    
    @transaction.atomic
    def create_quotation(self, quotation_data, quotation_items):
        """
        Create a new quotation with items
        
        Args:
            quotation_data: Dictionary with quotation data
            quotation_items: List of dictionaries with quotation item data
            
        Returns:
            Created Quotation instance
            
        Raises:
            ValueError: When validation fails
        """
        # Validate dealer exists
        if 'dealer_id' in quotation_data:
            dealer = self.dealer_repository.get(id=quotation_data['dealer_id'])
            if not dealer:
                raise ValueError(f"Dealer with ID {quotation_data['dealer_id']} not found")
        
        # Generate quotation number if not provided
        if 'quotation_number' not in quotation_data:
            today = timezone.now()
            prefix = 'QUO'
            quotation_data['quotation_number'] = f"{prefix}-{today.strftime('%Y%m%d')}-{today.timestamp():.0f}"
        
        # Set valid_until date if not provided (default: 30 days)
        if 'valid_until' not in quotation_data:
            quotation_data['valid_until'] = (timezone.now() + timedelta(days=30)).date()
            
        # Set status if not provided
        if 'status' not in quotation_data:
            quotation_data['status'] = QuotationStatus.PENDING
        
        # Validate quotation items
        for item in quotation_items:
            if 'item_id' not in item or not self.item_repository.get(id=item['item_id']):
                raise ValueError(f"Invalid item_id: {item.get('item_id')}")
        
        # Create quotation with items
        return self.repository.create_quotation_with_items(quotation_data, quotation_items)
    
    @transaction.atomic
    def update_quotation_status(self, quotation_id, status):
        """
        Update the status of a quotation
        
        Args:
            quotation_id: Quotation ID
            status: New quotation status
            
        Returns:
            Updated Quotation instance
            
        Raises:
            ValueError: When quotation not found or status invalid
        """
        if status not in [choice[0] for choice in QuotationStatus.choices]:
            raise ValueError(f"Invalid quotation status: {status}")
        
        quotation = self.repository.get(id=quotation_id)
        if not quotation:
            raise ValueError(f"Quotation with ID {quotation_id} not found")
            
        return self.repository.update_quotation_status(quotation_id, status)
    
    @transaction.atomic
    def mark_expired_quotations(self):
        """
        Mark all expired quotations as expired
        
        Returns:
            Number of quotations updated
        """
        return self.repository.mark_expired_quotations()
    
    @transaction.atomic
    def store_pdf(self, quotation_id, pdf_file):
        """
        Store the PDF file for a quotation
        
        Args:
            quotation_id: Quotation ID
            pdf_file: PDF file
            
        Returns:
            Updated Quotation instance
            
        Raises:
            ValueError: When quotation not found
        """
        quotation = self.repository.get(id=quotation_id)
        if not quotation:
            raise ValueError(f"Quotation with ID {quotation_id} not found")
            
        return self.repository.store_pdf(quotation_id, pdf_file)
    
    def delete_quotation(self, quotation_id):
        """
        Delete a quotation
        
        Args:
            quotation_id: Quotation ID
            
        Returns:
            Boolean indicating success
            
        Raises:
            ValueError: When quotation cannot be deleted
        """
        quotation = self.repository.get(id=quotation_id)
        if not quotation:
            return False
            
        # Quotations that are accepted or converted to orders cannot be deleted
        if quotation.status in [QuotationStatus.ACCEPTED, QuotationStatus.CONVERTED]:
            raise ValueError(f"Cannot delete quotation with status {quotation.status}")
            
        return self.repository.delete(quotation)