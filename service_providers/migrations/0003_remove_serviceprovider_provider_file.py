# Generated by Django 4.2.6 on 2023-11-13 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0002_alter_serviceprovider_provider_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceprovider',
            name='provider_file',
        ),
    ]