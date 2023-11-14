# Generated by Django 4.2.6 on 2023-11-14 06:07

from django.db import migrations, models
import users.models_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_users_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='image',
            field=models.ImageField(default='defaults/default_profile.jpg', null=True, upload_to=users.models_helpers.get_image_path),
        ),
    ]