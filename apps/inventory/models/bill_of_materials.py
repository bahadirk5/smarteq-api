from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel


class BillOfMaterials(BaseModel):
    """
    Defines the standard components (inputs) and quantities required to produce 
    an intermediate or final product. Holds the definition of "What is made from what?"
    """
    output_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='bom_outputs',
        verbose_name=_('Output Item'),
        help_text=_('The intermediate or final product being produced')
    )
    input_item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.CASCADE,
        related_name='bom_inputs',
        verbose_name=_('Input Item'),
        help_text=_('Component required for production')
    )
    quantity_required = models.DecimalField(
        _('Quantity Required'),
        max_digits=10,
        decimal_places=3,
        help_text=_('Amount of input item needed for one unit of output item')
    )
    unit_of_measure = models.CharField(_('Unit of Measure'), max_length=50)
    sequence = models.IntegerField(_('Sequence'), default=10, help_text=_('Order of assembly/production'))
    is_optional = models.BooleanField(_('Optional Component'), default=False,
                                    help_text=_('Can this component be omitted or substituted'))
    is_default = models.BooleanField(_('Default Component'), default=True,
                                   help_text=_('Is this the default component to use'))
    alternative_group = models.CharField(_('Alternative Group'), max_length=50, blank=True, null=True,
                                      help_text=_('Group identifier for alternative components'))

    class Meta(BaseModel.Meta):
        verbose_name = _('Bill of Materials')
        verbose_name_plural = _('Bills of Materials')
        ordering = ['output_item__name', 'sequence']
        unique_together = [['output_item', 'input_item']]

    def __str__(self):
        return f"{self.output_item.name} - {self.input_item.name} ({self.quantity_required} {self.unit_of_measure})"
