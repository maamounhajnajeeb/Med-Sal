# Generated by Django 4.2.6 on 2023-10-29 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('DOCTOR', 'Doctor'), ('DENTAL', 'Dental'), ('OPTICS', 'Optics'), ('NUTRITIONIST', 'Nutritionist'), ('HOME_CARE', 'Home Care'), ('PLASTIC_SURGERY', 'Plastic Surgery'), ('RADIOLOGIST', 'Radiologist'), ('AESTHETICS', 'Aesthetics'), ('PHARMACY', 'Pharmacy'), ('HOSPITAL', 'Hospital'), ('LAB', 'Lab'), ('CLINIC', 'Clinic')], max_length=20, unique=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Category',
            },
        ),
    ]
