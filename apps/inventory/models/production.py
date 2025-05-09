from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.common.models.base_model import BaseModel

User = get_user_model()


class Production(BaseModel):
    """
    Records a production event - when a recipe is executed to produce items.
    """
    recipe = models.ForeignKey(
        'inventory.Recipe',
        on_delete=models.PROTECT,
        related_name='productions',
        verbose_name=_('Recipe')
    )
    output_quantity = models.IntegerField(
        _('Output Quantity'),
        help_text=_('Actual quantity produced')
    )
    executed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='productions',
        verbose_name=_('Executed By')
    )
    execution_date = models.DateTimeField(_('Execution Date'), auto_now_add=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _('Production')
        verbose_name_plural = _('Productions')
        ordering = ['-execution_date']
    
    def __str__(self):
        return f"Production {self.id}: {self.recipe.name} - {self.output_quantity} {self.recipe.unit_of_measure}"
