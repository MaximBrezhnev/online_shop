from django.contrib import admin

from cart.models import ProductInCart, Order, OrderItem


@admin.register(ProductInCart)
class ProductInCart(admin.ModelAdmin):
    list_display = ("product", "user", "size", "number", )
    list_per_page = 20


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "surname", "name", "middle_name", "address", "status", "created_at")
    search_fields = ("id", "address")
    list_filter = ("status", )
    list_per_page = 20


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "number", "order", )
    search_fields = ("product__name", "order__id")
    list_per_page = 20