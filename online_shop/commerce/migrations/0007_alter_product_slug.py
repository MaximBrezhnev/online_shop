# Generated by Django 5.0.4 on 2024-04-21 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0006_alter_product_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=255, null=True),
        ),
    ]
