# Generated by Django 4.2.6 on 2024-01-09 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount_ammount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]