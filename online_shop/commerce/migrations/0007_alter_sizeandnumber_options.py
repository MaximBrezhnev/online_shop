# Generated by Django 5.0.4 on 2024-05-01 06:33
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("commerce", "0006_alter_productincart_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sizeandnumber",
            options={"ordering": ["size"]},
        ),
    ]
