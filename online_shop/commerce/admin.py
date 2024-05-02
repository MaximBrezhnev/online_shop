from django.contrib import admin

from commerce.models import Product, Category, Subcategory, SizeAndNumber, FavoriteProduct, ProductInCart, Order, \
    OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "price", "created_at",
                    "category", "subcategory")
    search_fields = ("name", )
    list_per_page = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


@admin.register(Subcategory)
class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


@admin.register(SizeAndNumber)
class SizeAndNumberAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "number", )
    search_fields = ("product__name", )
    list_per_page = 20


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ("product", "user", )
    list_per_page = 20


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

