# Generated by Django 4.2.6 on 2023-11-07 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0006_remove_serviceprovider_contact_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceprovider',
            name='provider_file',
        ),
    ]