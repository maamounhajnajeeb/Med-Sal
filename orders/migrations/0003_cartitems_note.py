# Generated by Django 4.2.6 on 2024-01-27 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='note',
            field=models.TextField(null=True),
        ),
    ]
