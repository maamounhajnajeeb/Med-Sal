# Generated by Django 4.2.6 on 2023-11-10 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0010_alter_serviceprovider_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceproviderlocations',
            name='service_provider_id',
        ),
        migrations.DeleteModel(
            name='ServiceProvider',
        ),
    ]
