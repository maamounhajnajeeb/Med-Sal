# Generated by Django 4.2.6 on 2023-11-10 05:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0009_serviceprovider_provider_file'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serviceprovider',
            options={},
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='account_status',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='bank_name',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='business_name',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='category',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='iban',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='provider_file',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='swift_code',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='serviceprovider',
            name='user',
        ),
    ]