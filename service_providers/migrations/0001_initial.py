# Generated by Django 4.2.6 on 2023-11-15 11:39

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import service_providers.helpers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('category', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('users_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('business_name', models.CharField(max_length=128, unique=True)),
                ('bank_name', models.CharField(max_length=128)),
                ('iban', models.CharField(max_length=40, unique=True)),
                ('swift_code', models.CharField(max_length=16, unique=True)),
                ('provider_file', models.FileField(upload_to=service_providers.helpers.upload_file)),
                ('account_status', models.CharField(choices=[('rejected', 'Rejected'), ('pending', 'Pending'), ('accepted', 'Accepted')], default='pending', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='accepted_services', to='users.admins')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_providerd', to='category.category')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='service_provider', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ServiceProvider',
                'verbose_name_plural': 'ServiceProviders',
            },
            bases=('users.users',),
        ),
        migrations.CreateModel(
            name='ServiceProviderLocations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('opening', models.TimeField()),
                ('closing', models.TimeField()),
                ('crew', models.CharField(max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('service_provider_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_providers.serviceprovider')),
            ],
            options={
                'verbose_name': 'ServiceProviderLocations',
                'verbose_name_plural': 'ServiceProviderLocations',
            },
        ),
    ]
