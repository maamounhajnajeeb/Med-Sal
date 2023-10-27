# Generated by Django 4.2.6 on 2023-10-27 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(choices=[('DOCTOR', 'Doctor'), ('DENTAL', 'Dental'), ('OPTICS', 'Optics'), ('NUTRITIONIST', 'Nutritionist'), ('HOME_CARE', 'Home Care'), ('PLASTIC_SURGERY', 'Plastic Surgery'), ('RADIOLOGIST', 'Radiologist'), ('AESTHETICS', 'Aesthetics'), ('PHARMACY', 'Pharmacy'), ('HOSPITAL', 'Hospital'), ('LAB', 'Lab'), ('CLINIC', 'Clinic')], max_length=20, unique=True),
        ),
    ]
