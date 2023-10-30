from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

class Category(models.Model):
    
    class Names(models.TextChoices):
        
        DOCTOR = ("DOCTOR","Doctor")
        DENTAL = ("DENTAL", "Dental") 
        OPTICS = ("OPTICS", "Optics") 
        NUTRITIONIST = ("NUTRITIONIST", "Nutritionist")
        HOME_CARE = ("HOME_CARE", "Home Care")
        PLASTIC_SURGERY = ("PLASTIC_SURGERY", "Plastic Surgery")
        RADIOLOGIST = ("RADIOLOGIST", "Radiologist")
        AESTHETICS = ("AESTHETICS", "Aesthetics")
        PHARMACY = ("PHARMACY", "Pharmacy")
        HOSPITAL = ("HOSPITAL", "Hospital")
        LAB = ("LAB", "Lab")
        CLINIC = ("CLINIC", "Clinic")
        
    name = models.CharField(max_length=20, choices=Names.choices, unique=True)
    parent = models.ForeignKey("category.Category", on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Category" 

    def __str__(self):
        return self.name


class MyCategory(TranslatableModel):
    name = models.CharField(max_length=20, unique=True)
    
    translations = TranslatedFields(
        ar_name = models.CharField(_("Name"), max_length=200)
    )

    def __unicode__(self):
        return self.name