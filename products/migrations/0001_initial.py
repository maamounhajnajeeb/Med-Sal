# Generated by Django 4.2.6 on 2023-11-02 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('service_providers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ar_title', models.CharField(max_length=128)),
                ('en_title', models.CharField(max_length=128)),
                ('ar_description', models.TextField()),
                ('en_description', models.TextField()),
                ('images', models.CharField(max_length=128)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.IntegerField()),
                ('discount', models.IntegerField(null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category')),
                ('service_provider_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_providers.serviceproviderlocations')),
            ],
        ),
    ]