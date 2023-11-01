from django.db import models


class Category(models.Model):
    
    name = models.JSONField(max_length=32, null=False)
    parent = models.ForeignKey("category.Category", on_delete=models.CASCADE, null=True)
    
