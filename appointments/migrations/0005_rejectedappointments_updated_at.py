# Generated by Django 4.2.6 on 2024-02-06 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_appointments_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='rejectedappointments',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
