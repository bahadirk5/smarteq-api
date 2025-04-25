from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class Department(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ["name"]
    
    def __str__(self):
        return self.name