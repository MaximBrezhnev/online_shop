# Generated by Django 5.0.4 on 2024-05-01 10:42
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("commerce", "0011_order_created_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="order",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="product",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="user",
        ),
        migrations.DeleteModel(
            name="Order",
        ),
        migrations.DeleteModel(
            name="OrderItem",
        ),
    ]
