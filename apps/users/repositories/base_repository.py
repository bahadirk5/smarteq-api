from typing import Type, List, Optional, Any, Dict, Union
from django.db.models import Model, QuerySet
from django.utils import timezone
import uuid

class BaseRepository:
    model_class: Type[Model] = None
    
    def __init__(self, model_class: Type[Model]):
        self.model_class = model_class
    
    def get_queryset(self) -> QuerySet:
        """
        Get base queryset. By default, excludes soft-deleted records.
        """
        queryset = self.model_class.objects.all()
        
        # Handle soft delete filtering if the model has deleted_at field
        if hasattr(self.model_class, 'deleted_at'):
            return queryset.filter(deleted_at__isnull=True)
        
        return queryset
    
    def get_by_id(self, id: Union[uuid.UUID, str]) -> Optional[Model]:
        """Get a record by its ID."""
        try:
            return self.get_queryset().get(id=id)
        except self.model_class.DoesNotExist:
            return None
    
    def list(self, include_deleted: bool = False, **filters) -> List[Model]:
        """
        List records with optional filters.
        
        Args:
            include_deleted: Whether to include soft-deleted records
            **filters: Additional filters
        """
        queryset = self.model_class.objects.all()
        
        # Handle soft delete filtering
        if hasattr(self.model_class, 'deleted_at') and not include_deleted:
            queryset = queryset.filter(deleted_at__isnull=True)
        
        return list(queryset.filter(**filters))
    
    def create(self, **data) -> Model:
        """Create a new record."""
        instance = self.model_class(**data)
        instance.save()
        return instance
    
    def update(self, instance: Model, **data) -> Model:
        """Update an existing record."""
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: Model, hard_delete: bool = False) -> bool:
        """
        Delete a record. By default, perform soft delete if the model supports it.
        
        Args:
            instance: The record to delete
            hard_delete: Whether to perform a hard delete regardless of soft delete support
        """
        if hasattr(instance, 'soft_delete') and not hard_delete:
            instance.soft_delete()
            return True
        else:
            instance.delete()
            return True
    
    def restore(self, instance: Model) -> Optional[Model]:
        """Restore a soft-deleted record."""
        if hasattr(instance, 'restore'):
            instance.restore()
            return instance
        return None