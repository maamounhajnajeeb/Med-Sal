# Generated by Django 4.2.6 on 2024-01-27 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_appointments_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointments',
            name='note',
            field=models.TextField(null=True),
        ),
    ]
