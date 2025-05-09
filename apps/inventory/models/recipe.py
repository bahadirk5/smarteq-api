from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class Recipe(BaseModel):
    """
    Defines manufacturing recipes - the standard components and quantities required 
    to produce an intermediate or final product.
    """
    name = models.CharField(_('Recipe Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    output_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Output Item'),
        help_text=_('The intermediate or final product being produced')
    )
    output_quantity = models.IntegerField(
        _('Output Quantity'),
        default=1,
        help_text=_('Amount produced per recipe execution')
    )
    unit_of_measure = models.CharField(_('Unit of Measure'), max_length=50)
    active = models.BooleanField(_('Active'), default=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.output_quantity} {self.unit_of_measure} of {self.output_item.name}"
