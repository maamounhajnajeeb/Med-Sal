# Generated by Django 4.2.6 on 2023-11-04 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceproviderlocations',
            name='location',
        ),
    ]