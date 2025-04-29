# apps/common/models/permission.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models.base_model import BaseModel

class Permission(BaseModel):
    """
    Sistem genelinde kullanılacak izinleri tanımlar.
    """
    name = models.CharField(_("Name"), max_length=100)
    code = models.CharField(_("Code"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    
    class Meta(BaseModel.Meta):
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")
        ordering = ["name"]
    
    def __str__(self):
        return self.name