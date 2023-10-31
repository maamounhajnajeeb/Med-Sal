from django.db import models
from django.utils.translation import gettext_lazy as _



class MyCategory(models.Model):
    name = models.JSONField(max_length = 32, null = True) 
    parent = models.ForeignKey("category.MyCategory", on_delete=models.CASCADE, null=True)
    
    def __unicode__(self):
        return self.name