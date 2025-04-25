from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from apps.users.models.department import Department

class Role(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    department = models.ForeignKey(
        Department, 
        related_name="roles", 
        on_delete=models.CASCADE,
        verbose_name=_("Department")
    )
    
    class Meta(BaseModel.Meta):
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"