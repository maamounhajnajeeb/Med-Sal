# Generated by Django 4.2.6 on 2023-11-11 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_remove_emailconfirmation_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailconfirmation',
            name='user_id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
