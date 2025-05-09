from django.db import models
from django.db import transaction
from apps.sales.models import Quotation, QuotationItem, QuotationStatus
from apps.common.repositories.base_repository import BaseRepository
from django.utils import timezone


class QuotationRepository(BaseRepository):
    """
    Repository for Quotation model operations.
    Follows the repository pattern for data access abstraction.
    """
    
    def __init__(self):
        super().__init__(Quotation)
    
    def get_by_number(self, quotation_number):
        """
        Get a quotation by its number
        
        Args:
            quotation_number: Quotation number
            
        Returns:
            Quotation instance or None if not found
        """
        try:
            return self.model.objects.get(quotation_number=quotation_number)
        except self.model.DoesNotExist:
            return None
    
    def get_by_dealer(self, dealer_id):
        """
        Get all quotations for a specific dealer
        
        Args:
            dealer_id: Dealer ID
            
        Returns:
            QuerySet of quotations
        """
        return self.model.objects.filter(dealer_id=dealer_id)
    
    def get_by_status(self, status):
        """
        Get all quotations with a specific status
        
        Args:
            status: Quotation status
            
        Returns:
            QuerySet of quotations
        """
        return self.model.objects.filter(status=status)
    
    def get_valid_quotations(self):
        """
        Get all valid quotations (not expired)
        
        Returns:
            QuerySet of valid quotations
        """
        today = timezone.now().date()
        return self.model.objects.filter(valid_until__gte=today)
    
    def get_expired_quotations(self):
        """
        Get all expired quotations
        
        Returns:
            QuerySet of expired quotations
        """
        today = timezone.now().date()
        return self.model.objects.filter(valid_until__lt=today)
    
    @transaction.atomic
    def create_quotation_with_items(self, quotation_data, items_data):
        """
        Create a quotation with its items
        
        Args:
            quotation_data: Quotation data
            items_data: List of quotation items data
            
        Returns:
            Created Quotation instance
        """
        # Create the quotation
        quotation = self.model.objects.create(**quotation_data)
        
        # Create quotation items
        for item_data in items_data:
            item_data['quotation'] = quotation
            QuotationItem.objects.create(**item_data)
        
        # Calculate total price
        quotation.calculate_total_price()
        
        return quotation
    
    @transaction.atomic
    def update_quotation_status(self, quotation_id, status):
        """
        Update the status of a quotation
        
        Args:
            quotation_id: Quotation ID
            status: New status
            
        Returns:
            Updated Quotation instance
        """
        quotation = self.get(id=quotation_id)
        quotation.status = status
        quotation.save()
        return quotation
    
    @transaction.atomic
    def mark_expired_quotations(self):
        """
        Mark all expired quotations as expired
        
        Returns:
            Number of quotations updated
        """
        today = timezone.now().date()
        count = 0
        
        # Get all quotations that are expired but not marked as expired
        expired_quotations = self.model.objects.filter(
            valid_until__lt=today,
            status__ne=QuotationStatus.EXPIRED
        )
        
        for quotation in expired_quotations:
            quotation.status = QuotationStatus.EXPIRED
            quotation.save()
            count += 1
        
        return count
    
    @transaction.atomic
    def store_pdf(self, quotation_id, pdf_file):
        """
        Store the PDF file for a quotation
        
        Args:
            quotation_id: Quotation ID
            pdf_file: PDF file
            
        Returns:
            Updated Quotation instance
        """
        quotation = self.get(id=quotation_id)
        quotation.pdf_file = pdf_file
        quotation.save()
        return quotation