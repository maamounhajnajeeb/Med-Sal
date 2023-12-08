# Generated by Django 4.2.6 on 2023-12-06 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='delivery', serialize=False, to='orders.orderitem')),
                ('delivered', models.BooleanField(default=False)),
            ],
        ),
    ]