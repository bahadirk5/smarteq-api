from apps.inventory.repositories.category_repository import CategoryRepository


class CategoryService:
    """
    Service class to handle business logic for Category operations.
    Uses CategoryRepository for data access.
    """
    
    def __init__(self):
        self.repository = CategoryRepository()
    
    def get_all_categories(self):
        """Get all categories"""
        return self.repository.get_all_categories()
    
    def get_category(self, category_id):
        """Get a category by its ID"""
        return self.repository.get_category_by_id(category_id)
    
    def get_root_categories(self):
        """Get all root categories (no parent)"""
        return self.repository.get_root_categories()
    
    def get_category_hierarchy(self, category_id=None):
        """Get a hierarchical structure of categories"""
        # If category_id is None, start from root categories
        if category_id is None:
            categories = self.repository.get_root_categories()
        else:
            categories = self.repository.get_subcategories(category_id)
            
        result = []
        for category in categories:
            subcategories = self.get_category_hierarchy(category.id)
            result.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'children': subcategories
            })
        
        return result
    
    def create_category(self, category_data):
        """Create a new category"""
        # Check if parent category already has a parent - only allow one level of nesting
        parent_id = category_data.get('parent_category_id')
        if parent_id:
            parent = self.repository.get_category_by_id(parent_id)
            if parent.parent_category is not None:
                raise ValueError('Categories can only be nested one level deep. This parent already has a parent.')
                
        return self.repository.create_category(category_data)
    
    def update_category(self, category_id, category_data):
        """Update an existing category"""
        # Check if parent category already has a parent - only allow one level of nesting
        parent_id = category_data.get('parent_category_id')
        if parent_id:
            parent = self.repository.get_category_by_id(parent_id)
            if parent.parent_category is not None:
                raise ValueError('Categories can only be nested one level deep. This parent already has a parent.')
            
            # Also check that we're not creating a cycle
            current = parent
            while current.parent_category is not None:
                if str(current.parent_category.id) == str(category_id):
                    raise ValueError('Cannot move a category to its own descendant')
                current = current.parent_category
                
        return self.repository.update_category(category_id, category_data)
    
    def delete_category(self, category_id):
        """Delete a category"""
        # Fetch the subcategories
        subcategories = self.repository.get_subcategories(category_id)
        
        # Recursive deletion of subcategories
        for subcategory in subcategories:
            # First recursively delete any deeper subcategories
            self.delete_category(subcategory.id)
        
        # Now it's safe to delete the category itself
        return self.repository.delete_category(category_id)
    
    def move_category(self, category_id, new_parent_id=None):
        """Move a category to a new parent"""
        # Prevent circular references
        if new_parent_id is not None:
            parent = self.repository.get_category_by_id(new_parent_id)
            current = parent
            # Check if the new parent is not a descendant of the category
            while current.parent_category is not None:
                if str(current.parent_category.id) == str(category_id):
                    raise ValueError('Cannot move a category to its own descendant')
                current = current.parent_category
        
        update_data = {'parent_category_id': new_parent_id}
        return self.repository.update_category(category_id, update_data)
