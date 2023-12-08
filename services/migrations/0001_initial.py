# Generated by Django 4.2.6 on 2023-12-06 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ar_title', models.CharField(max_length=127)),
                ('en_title', models.CharField(max_length=127)),
                ('ar_description', models.TextField()),
                ('en_description', models.TextField()),
                ('image', models.CharField(max_length=256)),
                ('price', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='category.category')),
            ],
        ),
    ]
