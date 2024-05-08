from django.contrib import admin

from commerce.models import Product, Category, Subcategory, SizeAndNumber, FavoriteProduct


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



