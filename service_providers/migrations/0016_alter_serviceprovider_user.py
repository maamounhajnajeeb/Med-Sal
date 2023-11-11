# Generated by Django 4.2.6 on 2023-11-10 06:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service_providers', '0015_alter_serviceprovider_provider_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprovider',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_provider', to=settings.AUTH_USER_MODEL),
        ),
    ]