# Generated by Django 4.2.6 on 2023-11-13 17:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import service_providers.helpers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service_providers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprovider',
            name='provider_file',
            field=models.FileField(null=True, upload_to=service_providers.helpers.upload_file),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='user',
            field=models.OneToOneField(default=200, on_delete=django.db.models.deletion.CASCADE, related_name='service_provider', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
