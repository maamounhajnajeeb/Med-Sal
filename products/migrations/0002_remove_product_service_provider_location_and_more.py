# Generated by Django 4.2.6 on 2023-11-25 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='service_provider_location',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='category.category'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
