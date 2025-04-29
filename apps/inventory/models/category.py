from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class Category(BaseModel):
    """
    Products/items classification model that supports hierarchical structure.
    """
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    parent_category = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name=_('Parent Category')
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """Returns the full hierarchical path of this category"""
        if self.parent_category:
            return f"{self.parent_category.full_path} > {self.name}"
        return self.name
