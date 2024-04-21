from django.core.validators import MinValueValidator
from django.db import models


class DisplayMixin:
    def __str__(self):
        return self.__getattribute__("name")


class Product(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    photo = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(to="Category", on_delete=models.PROTECT)
    subcategory = models.ForeignKey(to="Subcategory", on_delete=models.PROTECT)


class Category(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)


class Subcategory(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)


class SizeAndNumber(models.Model):
    value = models.CharField(max_length=10, blank=True, null=True)
    number = models.PositiveIntegerField()
    product = models.ForeignKey(to="Product", on_delete=models.CASCADE)

    def __str__(self):
        return self.__getattribute__("value")




