# Generated by Django 4.2.6 on 2023-11-11 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_users_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailconfirmation',
            name='id',
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='user_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]