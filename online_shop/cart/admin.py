from cart.models import Order
from cart.models import OrderItem
from cart.models import ProductInCart
from django.contrib import admin


@admin.register(ProductInCart)
class ProductInCartAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "size",
        "number",
    )
    list_per_page = 20


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "surname",
        "name",
        "middle_name",
        "address",
        "status",
        "created_at",
    )
    search_fields = ("id", "address")
    list_filter = ("status",)
    list_per_page = 20


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "number",
        "order",
    )
    search_fields = ("product__name", "order__id")
    list_per_page = 20
