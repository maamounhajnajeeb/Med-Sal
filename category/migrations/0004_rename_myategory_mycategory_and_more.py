# Generated by Django 4.2.6 on 2023-10-30 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0003_myategory_myategorytranslation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Myategory',
            new_name='MyCategory',
        ),
        migrations.RenameModel(
            old_name='MyategoryTranslation',
            new_name='MyCategoryTranslation',
        ),
        migrations.AlterModelOptions(
            name='mycategorytranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'my category Translation'},
        ),
        migrations.AlterModelTable(
            name='mycategorytranslation',
            table='category_mycategory_translation',
        ),
    ]
