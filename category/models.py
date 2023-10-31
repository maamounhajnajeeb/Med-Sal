from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields


class MyCategory(TranslatableModel):
    parent = models.ForeignKey("category.MyCategory", on_delete=models.CASCADE, null=True)
    
    translations = TranslatedFields(
        name = models.CharField(_("Name"), max_length=200)
    )

    def __unicode__(self):
        return self.name