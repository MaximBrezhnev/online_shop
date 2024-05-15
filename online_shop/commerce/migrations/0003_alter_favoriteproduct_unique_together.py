# Generated by Django 5.0.4 on 2024-04-29 14:18
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("commerce", "0002_favoriteproduct"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="favoriteproduct",
            unique_together={("user", "product")},
        ),
    ]
