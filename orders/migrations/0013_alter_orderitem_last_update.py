# Generated by Django 4.2.6 on 2023-12-07 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_rename_updated_at_orderitem_last_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='last_update',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
