# Generated by Django 4.2.6 on 2023-10-31 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
        ('service_providers', '0002_remove_serviceprovider_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='category.mycategory'),
        ),
    ]
