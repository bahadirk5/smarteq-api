from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class Project(BaseModel):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    # İleride departman, stok, sipariş, arıza gibi ilişkiler ManyToMany veya ForeignKey ile eklenebilir
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta(BaseModel.Meta):
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["name"]

    def __str__(self):
        return self.name
