from django.db import models

# Create your models here.
from django.db import models
from marshmallow import ValidationError

# Create your models here.

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

    name = models.CharField(max_length = 20, choices = Names.choices)

    class Meta:
        
        verbose_name = "Category"
        verbose_name_plural = "Category" 

    def __str__(self):
        return self.name
    
    
    
