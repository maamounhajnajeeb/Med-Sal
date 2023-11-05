from django.db import models


class Category(models.Model):
    
    name = models.JSONField(max_length=32, null=False)
    # parent = models.ForeignKey("Category", on_delete=models.CASCADE, null=True)
    
    # def __str__(self) -> str:
    #     return self.name["langs"]