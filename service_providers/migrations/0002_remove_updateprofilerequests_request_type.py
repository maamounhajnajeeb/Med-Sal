# Generated by Django 4.2.6 on 2023-11-20 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service_providers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='updateprofilerequests',
            name='request_type',
        ),
    ]
