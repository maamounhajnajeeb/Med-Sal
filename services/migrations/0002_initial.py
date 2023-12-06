# Generated by Django 4.2.6 on 2023-12-06 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service_providers', '0001_initial'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='provider_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='service_providers.serviceproviderlocations'),
        ),
    ]
