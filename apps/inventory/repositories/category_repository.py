from django.shortcuts import get_object_or_404
from apps.inventory.models import Category


class CategoryRepository:
    """
    Repository class for Category data access operations.
    Abstracts all database operations related to Category model.
    """
    
    def __init__(self):
        self.model = Category
    
    def get_all_categories(self):
        """Get all categories ordered by name"""
        return self.model.objects.all()
    
    def get_category_by_id(self, category_id):
        """Get a specific category by its ID"""
        return get_object_or_404(self.model, id=category_id)
    
    def get_root_categories(self):
        """Get all top-level categories (with no parent)"""
        return self.model.objects.filter(parent_category__isnull=True)
    
    def get_subcategories(self, parent_id):
        """Get all subcategories for a given parent category"""
        return self.model.objects.filter(parent_category_id=parent_id)
    
    def create_category(self, category_data):
        """Create a new category"""
        return self.model.objects.create(**category_data)
    
    def update_category(self, category_id, category_data):
        """Update an existing category"""
        category = self.get_category_by_id(category_id)
        
        for key, value in category_data.items():
            setattr(category, key, value)
        
        category.save()
        return category
    
    def delete_category(self, category_id):
        """Delete a category"""
        category = self.get_category_by_id(category_id)
        category.delete()
        return True
