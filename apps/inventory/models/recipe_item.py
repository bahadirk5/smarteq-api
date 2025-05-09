from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class RecipeItem(BaseModel):
    """
    Defines the individual input items and quantities for a recipe.
    A recipe can have multiple input items (raw materials or intermediate products).
    """
    recipe = models.ForeignKey(
        'inventory.Recipe',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Recipe')
    )
    input_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='recipe_inputs',
        verbose_name=_('Input Item'),
        help_text=_('Component required for production')
    )
    quantity_required = models.IntegerField(
        _('Quantity Required'),
        help_text=_('Amount of input item needed for one recipe execution')
    )
    unit_of_measure = models.CharField(_('Unit of Measure'), max_length=50)
    sequence = models.IntegerField(_('Sequence'), default=10, 
                                  help_text=_('Order of assembly/production'))
    is_optional = models.BooleanField(_('Optional Component'), default=False,
                                    help_text=_('Can this component be omitted'))
    notes = models.TextField(_('Notes'), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Recipe Item')
        verbose_name_plural = _('Recipe Items')
        ordering = ['recipe__name', 'sequence']
        unique_together = [['recipe', 'input_item']]
    
    def __str__(self):
        return f"{self.recipe.name} - {self.input_item.name} ({self.quantity_required} {self.unit_of_measure})"
